#!/usr/bin/env python3

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
      "app.main:app",
      reload=True,
      host=settings.HOST,
      port=settings.PORT,
    )