from fastapi import HTTPException, status

def admin_access(user, action, item):
    if user['role'] != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Only Admins can ${action} ${item}"
        )