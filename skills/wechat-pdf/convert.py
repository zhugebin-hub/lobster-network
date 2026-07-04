#!/usr/bin/env python3
"""
微信公众号文章转 PDF 工具
支持批量转换，自动提取标题作为文件名
"""

import asyncio
import sys
import os
import re
from pathlib import Path
from playwright.async_api import async_playwright


async def convert_wechat_article_to_pdf(url: str, output_dir: str = "./pdfs", timeout: int = 60000) -> str:
    """
    将微信公众号文章转换为 PDF
    
    Args:
        url: 微信公众号文章链接
        output_dir: 输出目录
        timeout: 超时时间（毫秒）
    
    Returns:
        PDF 文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"正在访问：{url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            
            # 等待页面内容加载
            await page.wait_for_timeout(3000)
            
            # 尝试获取文章标题
            title = await extract_title(page)
            if not title:
                title = "未知标题"
            
            print(f"文章标题：{title}")
            
            # 清理不需要的元素
            await clean_page(page)
            
            # 生成 PDF
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
            safe_title = safe_title.replace(" ", "_")
            if len(safe_title) > 80:
                safe_title = safe_title[:80]
            
            pdf_path = os.path.join(output_dir, f"{safe_title}.pdf")
            
            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "15mm",
                    "bottom": "15mm",
                    "left": "15mm",
                    "right": "15mm"
                }
            )
            
            print(f"✅ PDF 已保存：{pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ 转换失败：{e}")
            raise
        finally:
            await browser.close()


async def extract_title(page) -> str:
    """提取文章标题"""
    try:
        # 尝试多种选择器获取标题
        selectors = [
            "#activity-name",
            ".rich_media_title",
            "h1.rich_media_title",
            "title"
        ]
        
        for selector in selectors:
            try:
                if selector == "title":
                    title = await page.title()
                    if title and title != "微信公众平台":
                        return title.strip()
                else:
                    element = await page.query_selector(selector)
                    if element:
                        title = await element.inner_text()
                        if title.strip():
                            return title.strip()
            except:
                continue
        
        return ""
    except:
        return ""


async def clean_page(page):
    """清理页面不需要的元素"""
    try:
        # 隐藏不需要的元素
        selectors_to_hide = [
            "#js_pc_qr_code",      # PC 二维码
            "#js_article_comment", # 评论
            ".qr_code_pc",         # 二维码
            "#js_share_source",    # 分享来源
            ".rich_media_tool",    # 工具栏
            "#js_pc_qr_code_img",  # PC 二维码图片
            ".original_primary_card", # 原创声明
        ]
        
        for selector in selectors_to_hide:
            try:
                await page.evaluate(f"""
                    const el = document.querySelector('{selector}');
                    if (el) el.style.display = 'none';
                """)
            except:
                pass
        
        # 确保内容区域可见
        await page.evaluate("""
            const content = document.querySelector('#js_content');
            if (content) {
                content.style.visibility = 'visible';
                content.style.opacity = '1';
            }
        """)
        
    except Exception as e:
        print(f"清理页面时出错：{e}")


async def convert_batch(urls: list, output_dir: str = "./pdfs"):
    """批量转换"""
    results = []
    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] 处理：{url}")
        try:
            pdf_path = await convert_wechat_article_to_pdf(url, output_dir)
            results.append({"url": url, "pdf": pdf_path, "status": "success"})
        except Exception as e:
            print(f"❌ 失败：{e}")
            results.append({"url": url, "pdf": None, "status": "error", "error": str(e)})
        
        # 添加延迟避免被限制
        if i < len(urls) - 1:
            await asyncio.sleep(2)
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="微信公众号文章转 PDF 工具")
    parser.add_argument("urls", nargs="+", help="微信公众号文章链接")
    parser.add_argument("-o", "--output", default="./pdfs", help="输出目录")
    
    args = parser.parse_args()
    
    print(f"微信公众号文章转 PDF 工具")
    print(f"输出目录：{args.output}")
    print(f"{'='*50}")
    
    results = asyncio.run(convert_batch(args.urls, args.output))
    
    print(f"\n{'='*50}")
    print(f"转换完成！")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"成功：{success}/{len(results)}")


if __name__ == "__main__":
    main()
