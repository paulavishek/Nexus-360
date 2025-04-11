import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage, ChatAnalytics
from .utils.chatbot_service import ChatbotService

class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time chat functionality
    """
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Check authentication
        if not self.scope.get('user') or not self.scope['user'].is_authenticated:
            await self.close()
            return
            
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            # Parse the message
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')
            history = text_data_json.get('history', [])
            selected_model = text_data_json.get('model', 'gemini')
            refresh_data = text_data_json.get('refresh_data', False)
            session_id = text_data_json.get('session_id')
            message_id = text_data_json.get('message_id')
            sheet_name = text_data_json.get('sheet_name', '')
            
            if not message or not session_id:
                return
                
            # Get the user from the scope
            user = self.scope['user']
            
            # Send typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'status': 'typing'
                }
            )
            
            # Save the user message
            chat_session = await self.get_or_create_session(user, session_id)
            
            await self.save_message(chat_session, 'user', message)
            
            # Get response from chatbot in a non-blocking way
            context = None
            if sheet_name:
                context = f"Focus on data from the '{sheet_name}' sheet for this query."
                
            # Create a task to get the response
            response_data = await self.get_chatbot_response(message, history, context, selected_model, refresh_data)
            
            # Save bot's response
            await self.save_message(
                chat_session, 
                'assistant', 
                response_data['response'], 
                response_data.get('source')
            )
            
            # Update analytics
            await self.update_analytics(user, response_data.get('source'))
            
            # Send bot message to WebSocket
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bot_message',
                    'message': response_data['response'],
                    'source': response_data.get('source'),
                    'message_id': message_id,
                    'sheet_name': sheet_name
                }
            )
            
        except Exception as e:
            # Send error message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bot_message',
                    'message': f"Sorry, an error occurred: {str(e)}",
                    'source': 'error'
                }
            )
            print(f"WebSocket error: {str(e)}")
    
    async def typing_indicator(self, event):
        """
        Send typing indicator to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'status': event['status']
        }))
    
    async def bot_message(self, event):
        """
        Send bot message to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'message',
            'sender': 'assistant',
            'message': event['message'],
            'source': event.get('source'),
            'message_id': event.get('message_id'),
            'sheet_name': event.get('sheet_name')
        }))
        
        # After sending the message, hide the typing indicator
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'status': 'idle'
        }))

    @database_sync_to_async
    def get_or_create_session(self, user, session_id):
        """
        Get or create a chat session
        """
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            return ChatSession.objects.create(user=user)

    @database_sync_to_async
    def save_message(self, session, role, content, model=None):
        """
        Save a message to the database
        """
        message = ChatMessage.objects.create(
            session=session,
            role=role,
            content=content,
            model=model
        )
        
        # Update session's last activity
        session.save()  # This will update the updated_at field
        
        return message
        
    @database_sync_to_async
    def update_analytics(self, user, source):
        """
        Update analytics data
        """
        from django.utils import timezone
        
        today = timezone.now().date()
        analytics, _ = ChatAnalytics.objects.get_or_create(user=user, date=today)
        analytics.messages_sent += 1
        
        # Update the model counter
        if source == 'gemini':
            analytics.gemini_requests += 1
        elif source in ['openai', 'openai-fallback']:
            analytics.openai_requests += 1
            
        analytics.save()
    
    async def get_chatbot_response(self, message, history, context, selected_model, refresh_data):
        """
        Get response from chatbot service asynchronously
        """
        # This needs to run in a thread pool since it's blocking I/O
        loop = asyncio.get_event_loop()
        
        def _get_response():
            # Create a new ChatbotService instance
            chatbot = ChatbotService()
            
            # Override default model if needed
            if selected_model == 'openai':
                # Swap OpenAI to be primary
                temp = chatbot.gemini_client
                chatbot.gemini_client = chatbot.openai_client
                chatbot.openai_client = temp
                
            # Call the service
            return chatbot.get_response(message, context, history, use_cache=not refresh_data)
        
        # Run the blocking operation in a thread pool
        return await loop.run_in_executor(None, _get_response)