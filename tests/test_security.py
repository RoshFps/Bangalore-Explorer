import unittest

from explorer.security import hash_password, validate_signup, verify_password


class PasswordTests(unittest.TestCase):
    def test_hash_and_verify(self):
        h = hash_password("s3cure-pass")
        self.assertTrue(h.startswith("scrypt$"))
        self.assertNotIn("s3cure-pass", h)
        self.assertTrue(verify_password("s3cure-pass", h))
        self.assertFalse(verify_password("wrong", h))

    def test_salted(self):
        self.assertNotEqual(hash_password("same"), hash_password("same"))

    def test_garbage_hash(self):
        self.assertFalse(verify_password("x", "1234"))
        self.assertFalse(verify_password("x", "md5$a$b$c$d$e"))


class SignupValidationTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(validate_signup("roshan", "r@example.com", "longenough", "longenough"), [])

    def test_problems(self):
        errs = validate_signup("a", "not-an-email", "short", "different")
        self.assertEqual(len(errs), 4)


if __name__ == "__main__":
    unittest.main()
