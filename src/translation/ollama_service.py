"""
Ollama Service Module for managing Ollama models and API interactions
ใช้สำหรับดึงรายการ models และจัดการการเชื่อมต่อ Ollama
"""

import requests
import json
from typing import Dict, List, Optional


class OllamaService:
    """Service สำหรับจัดการ Ollama API และ models"""
    
    def __init__(self, host: str = "localhost", port: int = 11434):
        """
        เริ่มต้น Ollama Service
        
        Args:
            host (str): Ollama server host
            port (int): Ollama server port
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.tags_url = f"{self.base_url}/api/tags"
        self.session = requests.Session()
        self.timeout = 10
        
    def is_available(self) -> bool:
        """ตรวจสอบว่า Ollama พร้อมใช้งานหรือไม่"""
        try:
            response = self.session.get(self.tags_url, timeout=self.timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> List[Dict]:
        """
        ดึงรายการ models ที่มีอยู่ใน Ollama
        
        Returns:
            List[Dict]: รายการ models พร้อมข้อมูล
        """
        try:
            response = self.session.get(self.tags_url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                return models
            else:
                print(f"❌ Error fetching models: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            return []
    
    def get_model_names(self) -> List[str]:
        """
        ดึงรายชื่อ models เฉพาะชื่อ
        
        Returns:
            List[str]: รายชื่อ models
        """
        models = self.get_available_models()
        return [model.get('name', '') for model in models if model.get('name')]
    
    def get_vision_models(self) -> List[str]:
        """
        ดึงรายการ models ที่รองรับ vision (มี 'vision' ในชื่อ)
        
        Returns:
            List[str]: รายชื่อ vision models
        """
        model_names = self.get_model_names()
        # กรองหา models ที่น่าจะรองรับ vision
        vision_models = []
        for name in model_names:
            # ตรวจสอบ keywords ที่บ่งบอกว่าเป็น vision model
            vision_keywords = ['vision', 'vlm', 'multimodal', 'llava', 'gemma']
            if any(keyword in name.lower() for keyword in vision_keywords):
                vision_models.append(name)
        
        return vision_models if vision_models else model_names  # fallback ถ้าไม่เจอ
    
    def get_text_models(self) -> List[str]:
        """
        ดึงรายการ models สำหรับ text generation/translation
        
        Returns:
            List[str]: รายชื่อ text models
        """
        # สำหรับตอนนี้ return ทุก model เพราะส่วนใหญ่สามารถใช้แปลได้
        return self.get_model_names()
    
    def get_default_models(self) -> Dict[str, str]:
        """
        ได้ default models สำหรับ vision และ translation
        
        Returns:
            Dict[str, str]: {'vision': model_name, 'translation': model_name}
        """
        vision_models = self.get_vision_models()
        text_models = self.get_text_models()
        
        # เลือก default models
        default_vision = "gemma3:4b"  # current default
        default_translation = "gemma3:4b"  # current default
        
        # ถ้ามี models อื่นให้เลือกตามลำดับความสำคัญ
        if vision_models:
            for preferred in ["gemma3:4b", "llava", "gemma"]:
                for model in vision_models:
                    if preferred in model.lower():
                        default_vision = model
                        break
                if default_vision != "gemma3:4b":
                    break
            if default_vision == "gemma3:4b" and "gemma3:4b" not in vision_models:
                default_vision = vision_models[0]
        
        if text_models:
            for preferred in ["gemma3:4b", "gemma", "llama"]:
                for model in text_models:
                    if preferred in model.lower():
                        default_translation = model
                        break
                if default_translation != "gemma3:4b":
                    break
            if default_translation == "gemma3:4b" and "gemma3:4b" not in text_models:
                default_translation = text_models[0]
        
        return {
            'vision': default_vision,
            'translation': default_translation
        }


# Singleton instance สำหรับใช้ร่วมกัน
ollama_service = OllamaService()


if __name__ == "__main__":
    # ทดสอบ Ollama Service
    service = OllamaService()
    
    print("🔍 ทดสอบ Ollama Service")
    print(f"📡 การเชื่อมต่อ: {'✅ เชื่อมต่อได้' if service.is_available() else '❌ เชื่อมต่อไม่ได้'}")
    
    if service.is_available():
        models = service.get_available_models()
        print(f"📦 พบ {len(models)} models:")
        for model in models:
            print(f"   - {model.get('name', 'Unknown')}")
        
        print(f"\n👁️ Vision models: {service.get_vision_models()}")
        print(f"💬 Text models: {service.get_text_models()}")
        print(f"⚙️ Default models: {service.get_default_models()}")
    else:
        print("❌ กรุณาตรวจสอบ:")
        print("   1. Ollama กำลังทำงาน")
        print("   2. Ollama ทำงานบน port 11434")
        print("   3. สั่งรัน: ollama serve")