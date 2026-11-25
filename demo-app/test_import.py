try:
    from main import app
    print("✅ 导入成功")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")