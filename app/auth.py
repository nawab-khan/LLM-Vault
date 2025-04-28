from fastapi import Request, HTTPException, status

def get_current_user(request: Request):
    user_header = request.headers.get("x-auth-user")
    if not user_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {"sub": user_header}
