"""
SQL Generation Agent - Converts natural language to ClickHouse SQL
"""
import re
from typing import Optional

from ..integrations.openai_client import openai_client
from ..prompts.sql_prompts import get_sql_generation_prompt, get_topic_detail_prompt
from ..prompts.schema_prompts import get_schema_info


class SqlAgent:
    """
    Main SQL generation agent that converts natural language queries to ClickHouse SQL
    """
    
    def __init__(self):
        self.client = openai_client
    
    async def convert_to_sql(self, natural_query: str) -> str:
        """
        Convert natural language query to ClickHouse SQL
        
        Args:
            natural_query: User's natural language query
            
        Returns:
            Generated SQL query string
            
        Raises:
            Exception: If conversion fails or OpenAI client is not available
        """
        try:
            print("Getting schema information...")
            schema_info = get_schema_info()
            
            print("Building SQL generation prompt...")
            prompt = get_sql_generation_prompt(natural_query, schema_info)
            
            print(f"Prompt: {prompt}")
            print("Calling OpenAI API...")
            
            if not self.client.is_available():
                raise Exception("OpenAI client not initialized - check API key")
            
            # Generate SQL using OpenAI
            response = await self.client.generate_completion(prompt)
            
            # Clean up the response (remove markdown formatting if present)
            sql = self._clean_sql_response(response)
            
            print(f"OpenAI returned SQL: {sql}")
            return sql
            
        except Exception as e:
            print(f"ERROR in convert_to_sql: {type(e).__name__}: {str(e)}")
            raise Exception(f"Error converting to SQL: {type(e).__name__}: {str(e)}")
    
    async def generate_topic_detail_sql(self, topic_id: int, time_range: str = "7d", 
                                       stat_type: str = "all", country: str = "all") -> str:
        """
        Generate SQL for topic detail queries
        
        Args:
            topic_id: ID of the topic to analyze
            time_range: Time range for analysis (1h, 6h, 24h, 7d, 30d)
            stat_type: Type of statistics (all, search_volume, mentions, etc.)
            country: Country filter (all, US, CA, etc.)
            
        Returns:
            Generated SQL query string
        """
        try:
            print(f"Generating topic detail SQL for topic_id: {topic_id}")
            
            schema_info = get_schema_info()
            prompt = get_topic_detail_prompt(topic_id, time_range, stat_type, country, schema_info)
            
            print(f"Generated topic query prompt")
            
            if not self.client.is_available():
                raise Exception("OpenAI client not initialized - check API key")
            
            response = await self.client.generate_completion(prompt)
            sql = self._clean_sql_response(response)
            
            print(f"Generated SQL for topic: {sql}")
            return sql
            
        except Exception as e:
            print(f"ERROR in generate_topic_detail_sql: {type(e).__name__}: {str(e)}")
            raise Exception(f"Error generating topic detail SQL: {type(e).__name__}: {str(e)}")
    
    def _clean_sql_response(self, response: str) -> str:
        """
        Clean OpenAI response to extract pure SQL
        
        Args:
            response: Raw response from OpenAI
            
        Returns:
            Cleaned SQL query
        """
        # Remove markdown code block formatting
        sql = re.sub(r'```sql\n?', '', response)
        sql = re.sub(r'\n?```', '', sql)
        
        # Strip whitespace
        sql = sql.strip()
        
        return sql


# Global instance
sql_agent = SqlAgent()