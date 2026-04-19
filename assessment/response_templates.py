from __future__ import annotations


_TITLES = {
    "th": {
        "qa": "คำตอบ TRL",
        "assessment": "ผลการประเมิน TRL",
    },
    "en": {
        "qa": "TRL Answer",
        "assessment": "TRL Assessment",
    },
}

_MESSAGES = {
    "auth_error": {
        "th": {
            "qa": "ขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานของคุณได้อย่างปลอดภัย กรุณาเข้าสู่ระบบอีกครั้ง",
            "assessment": "ขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานสำหรับการประเมิน TRL ได้ กรุณาเข้าสู่ระบบอีกครั้ง",
        },
        "en": {
            "qa": "Sorry, we could not verify your access securely. Please sign in again.",
            "assessment": "Sorry, we could not verify your access for TRL assessment securely. Please sign in again.",
        },
    },
    "validation_error": {
        "th": {
            "qa": "ขออภัย ขณะนี้ระบบรองรับเฉพาะข้อความสำหรับคำถาม กรุณาพิมพ์คำถามที่ต้องการสอบถามแล้วผมจะช่วยต่อให้ครับ",
            "assessment": "ขออภัย ขณะนี้ระบบรองรับเฉพาะข้อมูลแบบข้อความสำหรับการประเมิน TRL กรุณาพิมพ์รายละเอียดหลักฐานที่มี",
        },
        "en": {
            "qa": "Sorry, the system currently accepts text questions only. Please type your question and I will help from there.",
            "assessment": "Sorry, the TRL assessment flow currently accepts text evidence only. Please provide your evidence in text form.",
        },
    },
    "technical_error": {
        "th": {
            "qa": "ขออภัย ระบบเกิดข้อขัดข้องทางเทคนิคระหว่างประมวลผลคำถาม กรุณาลองใหม่อีกครั้งในอีกสักครู่",
            "assessment": "ขออภัย ระบบเกิดข้อขัดข้องทางเทคนิคระหว่างประเมิน TRL กรุณาลองใหม่อีกครั้งในอีกสักครู่",
        },
        "en": {
            "qa": "Sorry, a technical problem occurred while processing your question. Please try again shortly.",
            "assessment": "Sorry, a technical problem occurred while assessing the TRL level. Please try again shortly.",
        },
    },
    "insufficient_evidence": {
        "th": {
            "qa": "ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอสำหรับตอบคำถามนี้อย่างมั่นใจ กรุณาระบุคำถามใหม่ให้เฉพาะเจาะจงเกี่ยวกับ TRL",
            "assessment": "หลักฐานสำหรับประเมิน TRL ยังไม่เพียงพอ กรุณาให้ข้อมูลเพิ่มเติมตามประเด็นที่ระบบร้องขอ",
        },
        "en": {
            "qa": "The available source evidence is not strong enough to answer this question confidently. Please ask a more specific TRL question.",
            "assessment": "There is not enough evidence to complete the TRL assessment yet. Please provide the additional details requested.",
        },
    },
    "off_topic": {
        "th": {
            "qa": "ขออภัย ขณะนี้ผมช่วยได้เฉพาะหัวข้อที่เกี่ยวข้องกับ Technology Readiness Level (TRL) เท่านั้น",
            "assessment": "ขออภัย การประเมินนี้รองรับเฉพาะข้อมูลที่เกี่ยวข้องกับ Technology Readiness Level (TRL) เท่านั้น",
        },
        "en": {
            "qa": "Sorry, I can currently help only with Technology Readiness Level (TRL) topics.",
            "assessment": "Sorry, this assessment supports Technology Readiness Level (TRL) information only.",
        },
    },
}


def get_response_title(mode: str = "qa", language: str = "th") -> str:
    return _TITLES.get(language, _TITLES["th"]).get(mode, _TITLES["th"]["qa"])


def get_response_message(message_key: str, mode: str = "qa", language: str = "th") -> str:
    language_bundle = _MESSAGES[message_key].get(language, _MESSAGES[message_key]["th"])
    return language_bundle[mode]
