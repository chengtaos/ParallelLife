"""人生画像数据模型 + 持久化管理器"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from ..config import Config


class ProfileStatus(str, Enum):
    CREATED = "created"
    GRAPH_BUILT = "graph_built"
    READY = "ready"
    FAILED = "failed"


@dataclass
class LifeProfile:
    profile_id: str
    name: str
    status: ProfileStatus
    created_at: str
    updated_at: str
    basic_info: Dict[str, Any] = field(default_factory=dict)
    extracted_text: str = ""
    graph_id: Optional[str] = None
    decision_ids: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, ProfileStatus) else self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "basic_info": self.basic_info,
            "graph_id": self.graph_id,
            "decision_ids": self.decision_ids,
            "entities": self.entities,
            "relationships": self.relationships,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifeProfile':
        status = data.get('status', 'created')
        if isinstance(status, str):
            status = ProfileStatus(status)
        return cls(
            profile_id=data['profile_id'],
            name=data.get('name', 'Unnamed'),
            status=status,
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            basic_info=data.get('basic_info', {}),
            extracted_text=data.get('extracted_text', ''),
            graph_id=data.get('graph_id'),
            decision_ids=data.get('decision_ids', []),
            entities=data.get('entities', []),
            relationships=data.get('relationships', []),
            error=data.get('error'),
        )


class ProfileManager:
    @classmethod
    def _ensure_dir(cls):
        os.makedirs(Config.PROFILES_DIR, exist_ok=True)

    @classmethod
    def _get_profile_dir(cls, profile_id: str) -> str:
        return os.path.join(Config.PROFILES_DIR, profile_id)

    @classmethod
    def _get_meta_path(cls, profile_id: str) -> str:
        return os.path.join(cls._get_profile_dir(profile_id), 'profile.json')

    @classmethod
    def _get_text_path(cls, profile_id: str) -> str:
        return os.path.join(cls._get_profile_dir(profile_id), 'input.txt')

    @classmethod
    def create(cls, name: str = "Unnamed") -> LifeProfile:
        cls._ensure_dir()
        profile_id = f"prof_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        profile = LifeProfile(
            profile_id=profile_id, name=name,
            status=ProfileStatus.CREATED,
            created_at=now, updated_at=now
        )
        os.makedirs(cls._get_profile_dir(profile_id), exist_ok=True)
        cls.save(profile)
        return profile

    @classmethod
    def save(cls, profile: LifeProfile):
        profile.updated_at = datetime.now().isoformat()
        with open(cls._get_meta_path(profile.profile_id), 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def get(cls, profile_id: str) -> Optional[LifeProfile]:
        meta_path = cls._get_meta_path(profile_id)
        if not os.path.exists(meta_path):
            return None
        with open(meta_path, 'r', encoding='utf-8') as f:
            return LifeProfile.from_dict(json.load(f))

    @classmethod
    def list_all(cls, limit: int = 50) -> List[LifeProfile]:
        cls._ensure_dir()
        profiles = []
        for pid in os.listdir(Config.PROFILES_DIR):
            p = cls.get(pid)
            if p:
                profiles.append(p)
        profiles.sort(key=lambda p: p.created_at, reverse=True)
        return profiles[:limit]

    @classmethod
    def delete(cls, profile_id: str) -> bool:
        import shutil
        d = cls._get_profile_dir(profile_id)
        if not os.path.exists(d):
            return False
        shutil.rmtree(d)
        return True

    @classmethod
    def save_input_text(cls, profile_id: str, text: str):
        with open(cls._get_text_path(profile_id), 'w', encoding='utf-8') as f:
            f.write(text)

    @classmethod
    def get_input_text(cls, profile_id: str) -> Optional[str]:
        p = cls._get_text_path(profile_id)
        if not os.path.exists(p):
            return None
        with open(p, 'r', encoding='utf-8') as f:
            return f.read()
