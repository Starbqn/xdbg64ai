"""
Memory AI Assistant

This module integrates AI capabilities into the memory debugger, allowing users
to interact with the memory editor using natural language commands.
"""

import anthropic
import json
import logging
import re
import os
import sys
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get API key from environment variable
anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
if not anthropic_key:
    logger.warning("ANTHROPIC_API_KEY environment variable not set")
    logger.info("AI assistant features will be disabled")
    # The application will still run, but AI features will be gracefully disabled
    print("=" * 80)
    print("NOTE: Anthropic API key not found. AI assistant features are disabled.")
    print("To enable AI features, set the ANTHROPIC_API_KEY environment variable.")
    print("See .env.example for configuration instructions.")
    print("=" * 80)

class MemoryAIAssistant:
    """
    AI assistant for memory debugging that understands natural language queries
    and can help with finding and modifying memory values.
    """
    
    def __init__(self, memory_editor, process_bridge):
        """
        Initialize the AI assistant with references to the memory editor and process bridge.
        
        Args:
            memory_editor: Reference to the memory editor instance
            process_bridge: Reference to the process bridge instance
        """
        self.memory_editor = memory_editor
        self.process_bridge = process_bridge
        self.current_process_id = None
        self.current_process_type = None
        self.conversation_history = []
        
        # Initialize Anthropic client if API key is available
        if anthropic_key:
            try:
                self.client = anthropic.Anthropic(api_key=anthropic_key)
                # Using model name from environment or default to a versioned model
                self.model = os.environ.get('ANTHROPIC_MODEL', 'claude-3-sonnet')
                logger.info("Initialized Anthropic client successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.client = None
        else:
            logger.error("Missing Anthropic API key, AI assistant will operate in fallback mode")
            self.client = None
            
    def _send_ai_request(self, prompt: str) -> str:
        """
        Send a request to the Anthropic Claude API and get the response.
        
        Args:
            prompt: The user's prompt to send to the AI
            
        Returns:
            The AI's response text
        """
        try:
            # Check if Anthropic client is available
            if not self.client:
                logger.warning("No Anthropic client available, using fallback response")
                return "AI assistant is not available. Please check your ANTHROPIC_API_KEY."
            
            # Prepare the conversation context with information about attached process
            system_prompt = "You are a memory debugging assistant specialized in helping users find and modify values in computer memory. "
            if self.current_process_id:
                system_prompt += f"The user is currently attached to process {self.current_process_id}. "
            
            # Add information about our expected JSON response format
            system_prompt += "When asked to interpret a request, respond with properly formatted JSON."
            
            # Create messages from conversation history (for context)
            messages = []
            for entry in self.conversation_history[-3:]:  # Include last 3 exchanges for context
                messages.append({"role": "user", "content": entry['user']})
                messages.append({"role": "assistant", "content": entry['assistant']})
            
            # Add the current user message
            messages.append({"role": "user", "content": prompt})
            
            # Send the request to Anthropic Claude
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=messages if messages else None,
                max_tokens=int(os.environ.get('ANTHROPIC_MAX_TOKENS', '1000')),
                temperature=float(os.environ.get('ANTHROPIC_TEMPERATURE', '0'))
            )
            
            # Extract the text from the response
            if response and response.content:
                for content_block in response.content:
                    if content_block.type == 'text':
                        return content_block.text
            
            return "I couldn't generate a proper response. Please try again."
            
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error communicating with the AI service: {str(e)}"
        except anthropic.APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            return "Error connecting to the AI service. Please check your network connection."
        except anthropic.RateLimitError as e:
            logger.error(f"Anthropic rate limit error: {e}")
            return "The AI service is currently busy. Please try again later."
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic authentication error: {e}")
            return "Authentication error with the AI service. Please check your API key."
        except Exception as e:
            logger.error(f"Unexpected error in AI request: {e}")
            return f"An unexpected error occurred: {str(e)}"
    
    def set_current_process(self, process_id: str, process_type: str) -> None:
        """
        Set the current process being debugged.
        
        Args:
            process_id: ID of the process
            process_type: Type of the process ('simulated' or 'real')
        """
        self.current_process_id = process_id
        self.current_process_type = process_type
    
    def _extract_memory_address(self, text: str) -> Optional[str]:
        """
        Extract a memory address from text.
        
        Args:
            text: Text to search for memory address
            
        Returns:
            Memory address as string or None if not found
        """
        # Look for patterns like 0x1234abcd or hexadecimal addresses
        address_matches = re.search(r'0x[0-9a-fA-F]+|[0-9a-fA-F]{8,16}', text)
        if address_matches:
            address = address_matches.group(0)
            # Ensure it has 0x prefix
            if not address.startswith('0x'):
                address = '0x' + address
            return address
        return None
    
    def _extract_numeric_value(self, text: str) -> Optional[Tuple[Any, str]]:
        """
        Extract a numeric value and its type from text.
        
        Args:
            text: Text to search for value
            
        Returns:
            Tuple of (value, type) or None if not found
        """
        # Look for integers
        int_matches = re.search(r'[-+]?\d+', text)
        if int_matches:
            return (int(int_matches.group(0)), "int")
        
        # Look for floats
        float_matches = re.search(r'[-+]?\d+\.\d+', text)
        if float_matches:
            return (float(float_matches.group(0)), "float")
        
        # Look for text in quotes for string values
        string_matches = re.search(r'"([^"]*)"', text)
        if string_matches:
            return (string_matches.group(1), "string")
        
        return None
    
    def handle_user_query(self, query: str, process_id: str, process_type: str) -> str:
        """
        Process a natural language query from the user and take appropriate actions.
        
        Args:
            query: The user's natural language query
            process_id: ID of the process to operate on
            process_type: Type of the process ('simulated' or 'real')
            
        Returns:
            Response to the user
        """
        self.set_current_process(process_id, process_type)
        
        # First, ask the AI to interpret the user's request
        interpretation_prompt = f"""
        Interpret the following memory debugging request:
        "{query}"
        
        If it's about finding a value, specify:
        - What value to search for
        - What data type it is (int, float, string)
        
        If it's about changing a value, specify:
        - The memory address to modify (if provided)
        - The value to change it to
        - What data type it is (int, float, string)
        
        Respond in JSON format with action, address (if applicable), value, and data_type fields.
        """
        
        ai_interpretation = self._send_ai_request(interpretation_prompt)
        logger.info(f"AI interpretation: {ai_interpretation}")
        
        # Extract structured information from the AI's interpretation
        try:
            # Extract JSON from the AI response (it might be wrapped in markdown code blocks)
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_interpretation, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group(1))
            else:
                # Try to find JSON without markdown formatting
                json_match = re.search(r'({.*})', ai_interpretation, re.DOTALL)
                if json_match:
                    structured_data = json.loads(json_match.group(1))
                else:
                    raise ValueError("Couldn't extract JSON from AI response")
            
            # Process the request based on the action
            if structured_data.get('action') == 'find':
                response = self._handle_find_value(structured_data.get('value'), 
                                                 structured_data.get('data_type', 'int'))
            elif structured_data.get('action') == 'change':
                response = self._handle_change_value(structured_data.get('address'),
                                                   structured_data.get('value'),
                                                   structured_data.get('data_type', 'int'))
            else:
                response = "I'm not sure what you want to do. Please try asking about finding or changing a memory value."
        
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error processing AI interpretation: {e}")
            
            # Fallback to pattern matching if AI interpretation failed
            if "find" in query.lower() or "search" in query.lower() or "where is" in query.lower():
                value_data = self._extract_numeric_value(query)
                if value_data:
                    value, data_type = value_data
                    response = self._handle_find_value(value, data_type)
                else:
                    response = "I couldn't determine what value you're looking for. Please specify a number or string in your query."
            
            elif "change" in query.lower() or "set" in query.lower() or "modify" in query.lower():
                address = self._extract_memory_address(query)
                value_data = self._extract_numeric_value(query)
                
                if address and value_data:
                    value, data_type = value_data
                    response = self._handle_change_value(address, value, data_type)
                else:
                    response = "I couldn't determine the address and value. Please specify them in your query."
            
            else:
                response = "I'm not sure what you want to do. Please try asking about finding or changing a memory value."
        
        # Update conversation history
        self.conversation_history.append({
            "user": query,
            "assistant": response
        })
        
        return response
    
    def _handle_find_value(self, value: Any, data_type: str) -> str:
        """
        Handle a request to find a value in memory.
        
        Args:
            value: The value to search for
            data_type: The data type of the value
            
        Returns:
            Response to the user
        """
        try:
            # Use the memory editor to scan for the value
            results = self.memory_editor.scan_memory(self.current_process_id, value, data_type)
            
            if not results:
                return f"I couldn't find the value {value} in the process memory."
            
            # Format the results
            if len(results) > 10:
                results_text = f"I found {len(results)} instances of {value} in memory. Here are the first 10 addresses:\n"
                for i, addr in enumerate(results[:10]):
                    results_text += f"- {addr}\n"
                results_text += f"\nThere are {len(results) - 10} more addresses. Use the memory view to see all results."
            else:
                results_text = f"I found {len(results)} instances of {value} in memory at these addresses:\n"
                for i, addr in enumerate(results):
                    results_text += f"- {addr}\n"
            
            return results_text
            
        except Exception as e:
            logger.error(f"Error finding value: {e}")
            return f"Error while searching for value: {str(e)}"
    
    def _handle_change_value(self, address: str, value: Any, data_type: str) -> str:
        """
        Handle a request to change a value in memory.
        
        Args:
            address: The memory address to modify
            value: The new value
            data_type: The data type of the value
            
        Returns:
            Response to the user
        """
        try:
            # Validate the address format
            if not address:
                return "Please specify a memory address to modify."
            
            # Use the memory editor to write the value
            success = self.memory_editor.write_process_memory(
                self.current_process_id, address, value, data_type)
            
            if success:
                return f"Successfully changed the value at {address} to {value}."
            else:
                return f"Failed to change the value at {address}. Please check if the address is valid."
            
        except Exception as e:
            logger.error(f"Error changing value: {e}")
            return f"Error while changing the value: {str(e)}"