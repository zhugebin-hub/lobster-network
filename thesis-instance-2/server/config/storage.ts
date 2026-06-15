/**
 * 存储服务配置
 * 支持阿里云OSS、AWS S3和本地存储
 * 迁移时只需修改环境变量即可切换存储后端
 */

import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { STORAGE_CONFIG } from "./env";
import * as fs from "fs";
import * as path from "path";

// S3/OSS客户端（懒加载）
let s3Client: S3Client | null = null;

function getS3Client(): S3Client {
  if (!s3Client) {
    const config: any = {
      region: STORAGE_CONFIG.region,
      credentials: {
        accessKeyId: STORAGE_CONFIG.accessKeyId,
        secretAccessKey: STORAGE_CONFIG.accessKeySecret,
      },
    };
    
    // 如果配置了自定义endpoint（阿里云OSS等）
    if (STORAGE_CONFIG.endpoint) {
      config.endpoint = STORAGE_CONFIG.endpoint;
      config.forcePathStyle = true; // 阿里云OSS需要
    }
    
    s3Client = new S3Client(config);
  }
  return s3Client;
}

/**
 * 上传文件到存储服务
 */
export async function uploadFile(
  key: string,
  data: Buffer | Uint8Array | string,
  contentType: string = "application/octet-stream"
): Promise<{ key: string; url: string }> {
  const normalizedKey = key.replace(/^\/+/, "");
  
  if (STORAGE_CONFIG.provider === "local") {
    return uploadToLocal(normalizedKey, data, contentType);
  }
  
  return uploadToS3(normalizedKey, data, contentType);
}

/**
 * 获取文件访问URL
 */
export async function getFileUrl(
  key: string,
  expiresIn: number = 3600
): Promise<{ key: string; url: string }> {
  const normalizedKey = key.replace(/^\/+/, "");
  
  if (STORAGE_CONFIG.provider === "local") {
    return getLocalFileUrl(normalizedKey);
  }
  
  return getS3FileUrl(normalizedKey, expiresIn);
}

// S3/OSS上传实现
async function uploadToS3(
  key: string,
  data: Buffer | Uint8Array | string,
  contentType: string
): Promise<{ key: string; url: string }> {
  const client = getS3Client();
  
  const command = new PutObjectCommand({
    Bucket: STORAGE_CONFIG.bucket,
    Key: key,
    Body: typeof data === "string" ? Buffer.from(data) : data,
    ContentType: contentType,
  });
  
  await client.send(command);
  
  // 构建公开访问URL
  let url: string;
  if (STORAGE_CONFIG.publicUrlPrefix) {
    url = `${STORAGE_CONFIG.publicUrlPrefix.replace(/\/+$/, "")}/${key}`;
  } else if (STORAGE_CONFIG.endpoint) {
    // 阿里云OSS格式
    url = `${STORAGE_CONFIG.endpoint}/${STORAGE_CONFIG.bucket}/${key}`;
  } else {
    // AWS S3格式
    url = `https://${STORAGE_CONFIG.bucket}.s3.${STORAGE_CONFIG.region}.amazonaws.com/${key}`;
  }
  
  return { key, url };
}

// S3/OSS获取签名URL
async function getS3FileUrl(
  key: string,
  expiresIn: number
): Promise<{ key: string; url: string }> {
  // 如果配置了公开URL前缀，直接返回
  if (STORAGE_CONFIG.publicUrlPrefix) {
    return {
      key,
      url: `${STORAGE_CONFIG.publicUrlPrefix.replace(/\/+$/, "")}/${key}`,
    };
  }
  
  // 否则生成签名URL
  const client = getS3Client();
  const command = new GetObjectCommand({
    Bucket: STORAGE_CONFIG.bucket,
    Key: key,
  });
  
  const url = await getSignedUrl(client, command, { expiresIn });
  return { key, url };
}

// 本地存储实现
async function uploadToLocal(
  key: string,
  data: Buffer | Uint8Array | string,
  contentType: string
): Promise<{ key: string; url: string }> {
  const filePath = path.join(STORAGE_CONFIG.localPath, key);
  const dir = path.dirname(filePath);
  
  // 确保目录存在
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  // 写入文件
  const buffer = typeof data === "string" ? Buffer.from(data) : Buffer.from(data);
  fs.writeFileSync(filePath, buffer);
  
  // 返回本地URL（需要配置静态文件服务）
  const url = `/uploads/${key}`;
  return { key, url };
}

// 本地文件URL
async function getLocalFileUrl(key: string): Promise<{ key: string; url: string }> {
  return {
    key,
    url: `/uploads/${key}`,
  };
}

// 兼容现有代码的导出
export const storagePut = uploadFile;
export const storageGet = getFileUrl;
