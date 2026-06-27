"""
测试消息安全模块
"""

import pytest
import json
import base64
from src.lobster_network.security import (
    generate_signature,
    verify_signature,
    sign_message,
    verify_message,
    SignedMessage,
    encrypt_message,
    decrypt_message,
    NodeAuthenticator,
    CRYPTOGRAPHY_AVAILABLE,
)


class TestSignature:
    """测试 SHA256 签名"""

    def test_generate_and_verify(self):
        """测试生成和验证签名"""
        payload = '{"msg_id": "test-001", "from": "n1", "to": "n2"}'
        signature = generate_signature(payload)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 = 64 hex chars
        assert verify_signature(payload, signature) is True

    def test_verify_tampered_payload(self):
        """测试篡改后的验证失败"""
        payload = '{"msg_id": "test-001"}'
        signature = generate_signature(payload)
        
        tampered = '{"msg_id": "test-002"}'
        assert verify_signature(tampered, signature) is False

    def test_different_secret(self):
        """测试不同密钥验证失败"""
        payload = '{"test": true}'
        sig1 = generate_signature(payload, secret="secret1")
        assert verify_signature(payload, sig1, secret="secret2") is False


class TestSignedMessage:
    """测试带签名的消息"""

    def test_sign_and_verify(self):
        """测试签名和验证"""
        msg = {"msg_id": "m1", "payload": {"task": "test"}}
        sm = SignedMessage.from_message(msg)
        
        signature = sm.sign()
        assert signature is not None
        assert sm.verify() is True

    def test_verify_without_signature(self):
        """测试无签名验证"""
        msg = {"msg_id": "m2"}
        sm = SignedMessage.from_message(msg)
        
        assert sm.verify() is False

    def test_to_dict_and_back(self):
        """测试序列化和反序列化"""
        msg = {"msg_id": "m3", "data": [1, 2, 3]}
        sm = SignedMessage.from_message(msg)
        sm.sign()
        
        d = sm.to_dict()
        assert "message" in d
        assert "signature" in d
        
        sm2 = SignedMessage.from_dict(d)
        assert sm2.verify() is True


@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography 库未安装")
class TestEncryption:
    """测试 AES 加密"""

    def test_encrypt_decrypt(self):
        """测试加密和解密"""
        plaintext = '{"secret": "data", "value": 42}'
        encrypted = encrypt_message(plaintext)
        
        assert isinstance(encrypted, str)
        assert encrypted != plaintext
        
        decrypted = decrypt_message(encrypted)
        assert decrypted == plaintext


@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="cryptography 库未安装")
class TestNodeAuthenticator:
    """测试节点身份认证"""

    def test_generate_and_verify_token(self):
        """测试令牌生成和验证"""
        auth = NodeAuthenticator(secret="test-secret")
        
        token = auth.generate_token("n1", expires_in=3600)
        assert isinstance(token, str)
        
        valid, node_id = auth.verify_token(token)
        assert valid is True
        assert node_id == "n1"

    def test_expired_token(self):
        """测试过期令牌"""
        auth = NodeAuthenticator()
        
        # 生成已过期的令牌
        token = auth.generate_token("n1", expires_in=-1)
        valid, _ = auth.verify_token(token)
        assert valid is False

    def test_wrong_signature(self):
        """测试签名错误的令牌"""
        auth1 = NodeAuthenticator(secret="secret1")
        auth2 = NodeAuthenticator(secret="secret2")
        
        token = auth1.generate_token("n1")
        valid, _ = auth2.verify_token(token)
        assert valid is False


class TestSignMessageHelper:
    """测试便捷函数"""

    def test_sign_message(self):
        """测试对消息签名"""
        msg = {"msg_id": "helper-001", "from": "a", "to": "b"}
        signed = sign_message(msg)
        
        assert "_signature" in signed
        assert "_signed_at" in signed
        assert verify_message(signed) is True

    def test_verify_message_no_signature(self):
        """测试无签名的消息验证失败"""
        msg = {"msg_id": "no-sig"}
        assert verify_message(msg) is False

    def test_verify_message_tampered(self):
        """测试篡改消息验证失败"""
        msg = {"msg_id": "tamper", "data": "original"}
        signed = sign_message(msg)
        
        # 篡改消息
        signed["data"] = "tampered"
        assert verify_message(signed) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
