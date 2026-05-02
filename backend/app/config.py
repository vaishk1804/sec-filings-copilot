from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  openai_api_key: str
  database_url: str
  edgar_user_agent: str = "SEC Filings Copilot dev@example.com"
  embedding_model: str = "text-embedding-3-small"
  llm_model:str = "gpt-4o-mini"
  chunk_size: int = 512 # tokens
  chunk_overlap: int = 128 # tokens
  retrieval_top_k: int = 5

  class Config:
    env_file = ".env"

settings=Settings()