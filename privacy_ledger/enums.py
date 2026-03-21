from enum import Enum

class Topic(str, Enum):
    LEGAL = "legal"            # Laws, regulations, government actions
    APPS = "apps"              # Specific applications or software
    SOCIAL = "social-media"    # Social platforms and networks
    BUSINESS = "business"      # Companies, corporate practices
    SECURITY = "security"      # Security incidents, breaches, vulnerabilities

class ImpactType(str, Enum):
    DATA_EXPOSURE = "data_exposure"
    ANONYMITY = "anonymity"
    BEHAVIORAL_TRACKING = "behavioral_tracking"
    LEGAL_PRECEDENT = "legal_precedent"
    MASS_SURVEILLANCE = "mass_surveillance"
    CONSENT_VIOLATION = "consent_violation"
    OTHER = "other"

class Scope(str, Enum):
    LOCAL = "local"
    NATIONAL = "national"
    GLOBAL = "global"

class Severity(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Platform(str, Enum):
    MOBILE = "mobile"
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    LINUX = "linux"
    WINDOWS = "windows"
    MAC = "mac"
