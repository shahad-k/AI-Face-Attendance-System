import sys
import traceback

try:
    import face_recognition
    print("Success")
except Exception as e:
    print("Error:", type(e))
    traceback.print_exc()
except SystemExit as e:
    print("SystemExit caught:", e)
    traceback.print_exc()
