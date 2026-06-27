"""
消息安全模块 - SHA256签名 + AES加密

提供：
1. 消息签名（HMAC-SHA256）
2. 消息加密/解密（AES-256-GCM）
3. 节点身份认证
"""

import hashlib
import hmac
import json
import os
import base64
from datetime import datetime
from typing import Dict, Optional, Tuple

from src.lobster_network.utils.logger import get_logger

logger = get_logger(__name__)

# ── 配置 ──────────────────────────────────────────────────

# 默认密钥（生产环境应从环境变量或配置文件读取）
DEFAULT_SECRET = os.environ.get("LOBSTER_SECRET_KEY", "lobster-network-default-secret-2026")

# ── SHA256 签名 ─────────────────────────────────────────


def generate_signature(payload: str, secret: str = DEFAULT_SECRET) -> str:
    """
    生成 HMAC-SHA256 签名
    
    Args:
        payload: 待签名的数据（通常是序列化后的消息）
        secret: 密钥
    
    Returns:
        str: 十六进制签名字符串
    """
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def verify_signature(payload: str, signature: str, secret: str = DEFAULT_SECRET) -> bool:
    """
    验证 HMAC-SHA256 签名
    
    Args:
        payload: 原始数据
        signature: 待验证的签名
        secret: 密钥
    
    Returns:
        bool: 签名是否有效
    """
    expected = generate_signature(payload, secret)
    return hmac.compare_digest(expected, signature)


class SignedMessage:
    """
    带签名的消息包装器
    
    用法:
        sm = SignedMessage.from_message(msg_dict)
        sm.sign()
        verified = sm.verify()
    """

    def __init__(self, message: Dict, signature: Optional[str] = None, timestamp: Optional[str] = None):
        self.message = message
        self.signature = signature
        self.timestamp = timestamp or datetime.now().isoformat()

    @classmethod
    def from_message(cls, message: Dict) -> "SignedMessage":
        """从消息字典创建"""
        return cls(message=message)

    def sign(self, secret: str = DEFAULT_SECRET) -> str:
        """
        对消息生成签名
        
        Returns:
            str: 签名字符串
        """
        payload = self._serialize()
        self.signature = generate_signature(payload, secret)
        return self.signature

    def verify(self, secret: str = DEFAULT_SECRET) -> bool:
        """
        验证消息签名
        
        Returns:
            bool: 验证是否通过
        """
        if not self.signature:
            logger.warning("消息缺少签名")
            return False

        payload = self._serialize()
        valid = verify_signature(payload, self.signature, secret)

        if not valid:
            logger.warning(f"消息签名验证失败: {self.message.get('msg_id', 'unknown')}")

        return valid

    def _serialize(self) -> str:
        """序列化消息（用于签名）"""
        # 使用稳定序列化：排序键，确保一致性
        return json.dumps(self.message, sort_keys=True, ensure_ascii=False)

    def to_dict(self) -> Dict:
        """转换为字典（用于传输）"""
        return {
            "message": self.message,
            "signature": self.signature,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SignedMessage":
        """从字典恢复"""
        return cls(
            message=data.get("message", {}),
            signature=data.get("signature"),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )


# ── AES 加密 ──────────────────────────────────────────────

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography 库未安装，AES加密功能不可用")


def derive_key(secret: str, salt: bytes = b"lobster-network-salt") -> bytes:
    """
    从密钥派生AES密钥（PBKDF2）
    
    Args:
        secret: 原始密钥
        salt: 盐值
    
    Returns:
        bytes: 32字节AES密钥
    """
    if CRYPTOGRAPHY_AVAILABLE:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(secret.encode("utf-8"))
    else:
        # 降级方案：使用SHA256哈希（不够安全，但可用）
        return hashlib.sha256((secret + salt.decode("utf-8")).encode("utf-8")).digest()


def encrypt_message(payload: str, secret: str = DEFAULT_SECRET) -> str:
    """
    加密消息（AES-256-GCM）
    
    Args:
        payload: 明文消息
        secret: 密钥
    
    Returns:
        str: Base64编码的密文
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("AES加密需要 cryptography 库，请运行: pip install cryptography")
        return payload  # 降级：返回明文

    key = derive_key(secret)
    iv = os.urandom(12)  # GCM推荐12字节IV

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    plaintext = payload.encode("utf-8")
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # 组合：IV + 密文 + 认证标签
    encrypted = iv + ciphertext + encryptor.tag

    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_message(encrypted_payload: str, secret: str = DEFAULT_SECRET) -> str:
    """
    解密消息（AES-256-GCM）
    
    Args:
        encrypted_payload: Base64编码的密文
        secret: 密钥
    
    Returns:
        str: 解密后的明文
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        logger.error("AES解密需要 cryptography 库")
        return encrypted_payload  # 降级：返回原文（假设是明文）

    key = derive_key(secret)
    encrypted = base64.b64decode(encrypted_payload)

    iv = encrypted[:12]
    tag = encrypted[-16:]
    ciphertext = encrypted[12:-16]

    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext.decode("utf-8")


# ── 节点身份认证 ────────────────────────────────────────────

class NodeAuthenticator:
    """
    节点身份认证器
    
    使用 HMAC-SHA256 生成/验证节点令牌（Token）
    """

    def __init__(self, secret: str = DEFAULT_SECRET):
        self.secret = secret

    def generate_token(self, node_id: str, expires_in: int = 3600) -> str:
        """
        生成节点认证令牌
        
        Args:
            node_id: 节点ID
            expires_in: 有效期（秒），默认1小时
        
        Returns:
            str: Base64编码的令牌
        """
        payload = {
            "node_id": node_id,
            "issued_at": datetime.now().isoformat(),
            "expires_in": expires_in,
        }

        payload_str = json.dumps(payload, sort_keys=True)
        signature = generate_signature(payload_str, self.secret)

        token_data = {
            "payload": payload,
            "signature": signature,
        }

        return base64.b64encode(json.dumps(token_data).encode("utf-8")).decode("utf-8")

    def verify_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        验证节点认证令牌
        
        Args:
            token: Base64编码的令牌
        
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 节点ID)
        """
        try:
            token_data = json.loads(base64.b64decode(token).decode("utf-8"))
            payload = token_data["payload"]
            signature = token_data["signature"]

            # 验证签名
            payload_str = json.dumps(payload, sort_keys=True)
            if not verify_signature(payload_str, signature, self.secret):
                return False, None

            # 检查过期
            issued_at = datetime.fromisoformat(payload["issued_at"])
            elapsed = (datetime.now() - issued_at).total_seconds()

            if elapsed > payload["expires_in"]:
                logger.warning(f"令牌已过期: {payload['node_id']}")
                return False, None

            return True, payload["node_id"]

        except Exception as e:
            logger.error(f"令牌验证失败: {e}")
            return False, None


# ── 便捷函数 ──────────────────────────────────────────────

def sign_message(message: Dict, secret: str = DEFAULT_SECRET) -> Dict:
    """
    对消息签名并附加签名到消息中
    
    Args:
        message: 原始消息字典
        secret: 密钥
    
    Returns:
        Dict: 带签名的消息（新增 _signature 字段）
    """
    payload = json.dumps(message, sort_keys=True, ensure_ascii=False)
    signature = generate_signature(payload, secret)
    message["_signature"] = signature
    message["_signed_at"] = datetime.now().isoformat()
    return message


def verify_message(message: Dict, secret: str = DEFAULT_SECRET) -> bool:
    """
    验证消息签名（从消息中提取 _signature 字段）
    
    Args:
        message: 带签名的消息字典
        secret: 密钥
    
    Returns:
        bool: 签名是否有效
    """
    signature = message.get("_signature")
    if not signature:
        return False

    # 临时移除签名字段进行验证
    message_copy = message.copy()
    del message_copy["_signature"]
    del message_copy["_signed_at"]

    payload = json.dumps(message_copy, sort_keys=True, ensure_ascii=False)
    return verify_signature(payload, signature, secret)


if __name__ == "__main__":
    # 测试
    print("═══ 消息安全模块测试 ═══")

    # 测试签名
    msg = {"msg_id": "test-001", "from": "n1", "to": "n2", "payload": {"task": "test"}}
    signed = sign_message(msg)
    print(f"签名后: {signed_msg}")

    verified = verify_message(signed_msg)
    print(f"验证结果: {verified}")

    # 测试加密
    encrypted = encrypt_message(json.dumps(msg))
    print(f"加密后: {encrypted[:50]}...")

    decrypted = decrypt_message(encrypted)
    print(f"解密后: {decrypted}")

    # 测试令牌
    auth = NodeAuthenticator()
    token = auth.generate_token("n1")
    print(f"生成令牌: {token[:50]}...")

    valid, node_id = auth.verify_token(token)
    print(f"验证令牌: {valid}, node_id={node_id}")
