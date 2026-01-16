from fastapi import APIRouter, HTTPException
from imagekitio import ImageKit
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/imagekit", tags=["imagekit"])

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)

class AuthResponse(BaseModel):
    token:str
    expire: int
    signature:str

@router.get("/auth", response_model=AuthResponse)
async def get_imagekit_auth():
    """
    Generate authentication parameters for ImageKit upload
    """  
    try:
        print(imagekit)
        auth_params = imagekit.helper.get_authentication_parameters()
        return AuthResponse(
            token=auth_params['token'],
            expire=auth_params['expire'],
            signature=auth_params['signature']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))