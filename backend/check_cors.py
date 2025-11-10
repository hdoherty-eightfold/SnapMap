import sys
sys.path.insert(0, '.')
from main import app

print("Checking CORS Configuration...")
print("=" * 50)

# Check middleware
print("\nUser Middleware:")
for idx, mw in enumerate(app.user_middleware):
    print(f"{idx + 1}. {mw}")
    if hasattr(mw, 'kwargs'):
        kwargs = mw.kwargs
        print(f"   Options: {kwargs}")
        if 'allow_origins' in kwargs:
            print(f"   Allowed Origins: {kwargs['allow_origins']}")

# Check if CORS middleware is present
cors_found = False
for mw in app.user_middleware:
    if 'CORS' in str(type(mw.cls)):
        cors_found = True
        print(f"\nCORS Middleware Found: {mw.cls}")
        if hasattr(mw, 'kwargs'):
            print(f"Configuration:")
            for key, value in mw.kwargs.items():
                print(f"  {key}: {value}")

if not cors_found:
    print("\nWARNING: No CORS middleware found!")

print("\n" + "=" * 50)
