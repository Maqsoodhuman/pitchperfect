from dotenv import load_dotenv
load_dotenv()

from app.storage import get_resume, save_resume

USER_A = "11111111-1111-1111-1111-111111111111"
USER_B = "22222222-2222-2222-2222-222222222222"

print("Test 1: save and retrieve resume")
save_resume(USER_A, "RESUME_A_VERSION_1")
resume = get_resume(USER_A)
assert resume == "RESUME_A_VERSION_1", f"got: {resume}"
print("  ✅ saved and retrieved")

print("\nTest 2: upsert updates existing resume")
save_resume(USER_A, "RESUME_A_VERSION_2")
resume = get_resume(USER_A)
assert resume == "RESUME_A_VERSION_2", f"got: {resume}"
print("  ✅ upsert works")

print("\nTest 3: unknown user returns None")
missing = get_resume("99999999-9999-9999-9999-999999999999")
assert missing is None, f"expected None, got: {missing}"
print("  ✅ None returned for unknown user")

print("\nTest 4: two users have isolated resumes")
save_resume(USER_B, "RESUME_B_VERSION_1")
assert get_resume(USER_A) == "RESUME_A_VERSION_2"
assert get_resume(USER_B) == "RESUME_B_VERSION_1"
print("  ✅ users are isolated")

print("\nstorage.py OK ✅")
