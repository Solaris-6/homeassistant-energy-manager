"""Constants for the Energy Manager integration."""

DOMAIN = "energy_manager"
NAME = "Energy Manager"
VERSION = "0.1.0"
MANIFEST = "manifest.json"

# Configuration keys
CONF_DEVICE = "device"
CONF_DEVICE_ID = "device_id"
CONF_AREA = "area"
CONF_ENTITY_ACTIVE = "entity_active"
CONF_PRIORITY = "priority"
CONF_THRESHOLD = "threshold_kW"
CONF_ISOSTERISIS = "isosterisis_s"

# Default values
DEFAULT_THRESHOLD_KW = 2.8
DEFAULT_ISOSTERISIS_S = 30
DEFAULT_PRIORITY = 50

# Power limits
MAX_POWER_KW = 3.0
MIN_POWER_KW = 0.0

# Modes
MODE_NORMAL = "normal"
MODE_SUMMER = "summer"
MODE_WINTER = "winter"
MODE_VACATION = "vacation"
MODE_NIGHT = "night"
MODE_FOTP = "fotovoltaico"
MODE_EMERGENCY = "emergenza"

# Priority constants
PRIORITY_HIGHEST = 100
PRIORITY_HIGH = 95
PRIORITY_MEDIUM = 70
PRIORITY_LOW = 40
PRIORITY_LOWEST = 10

# Status states
STATUS_OK = "ok"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"
STATUS_ERROR = "error"

# Device states
STATE_ON = "on"
STATE_OFF = "off"
STATE_PAUSED = "paused"
STATE_UNKNOWN = "unknown"

