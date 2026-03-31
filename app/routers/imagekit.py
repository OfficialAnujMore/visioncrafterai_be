from fastapi import APIRouter, HTTPException, Depends
from imagekitio import ImageKit
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app.schemas.common import ApiResponse
from app.utils.security import get_current_user_from_cookie

load_dotenv()

router = APIRouter(prefix="/api/imagekit", tags=["imagekit"])

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
)

class ImageKitAuthResponse(BaseModel):
    token: str
    expire: int
    signature: str

@router.get("/auth", response_model=ApiResponse[ImageKitAuthResponse])
async def get_imagekit_auth(
    current_user: dict = Depends(get_current_user_from_cookie)
):
    """
    Generate authentication parameters for ImageKit upload.
    Requires authentication via JWT token from cookies.
    """  
    try:
        auth_params = imagekit.helper.get_authentication_parameters()
        imagekit_response = ImageKitAuthResponse(
            token=auth_params['token'],
            expire=auth_params['expire'],
            signature=auth_params['signature']
        )
        
        return ApiResponse(
            success=True,
            data=imagekit_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))