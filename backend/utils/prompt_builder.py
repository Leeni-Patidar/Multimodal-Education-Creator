def build_text_prompt(topic, level):
    return f"""
Explain the concept: {topic}

Difficulty Level: {level}

Format:
**1. Definition**
**2. Working**
**3. Examples**
**4. Real-life applications**
**5. Bullet Notes**
**6. Step-by-step explanation**
"""

def build_image_prompt(topic, style):
    return f"{style} educational diagram of {topic}, clean, labeled, high quality"