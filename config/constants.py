"""
Application Constants
"""

# Chart Settings
CHART_H = 330
PAPER = "rgba(0,0,0,0)"
PLOT = "rgba(0,0,0,0)"

# Team Performance Constants
DAILY_TARGET_HOURS = 8
LATE_ENTRY_THRESHOLD = 24

# Scheduler Constants
ALL_DAYS = ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

TRACK_COLORS = {
    "AI": "#6366f1",
    "Embedded": "#f59e0b",
    "Testing": "#10b981",
    "Full Stack": "#22d3ee",
    "Flutter": "#ec4899",
    "Data Analysis": "#f97316",
    "Cyber": "#ef4444",
}

# B2C Arabic Evaluation Columns
EVAL_AR_COLS = [
    "مدى وضوح الشرح",
    "تنظيم وترتيب الأفكار",
    "التفاعل مع الطلاب",
    "الاجابه على الاسئله",
    "ملائمة المحتوى لأهداف السيشن",
    "درجة التعمق/المستوى المناسب للطلاب",
    "استخدام أمثلة عملية",
]

# Yes/No Normalization Sets
YES_VALUES = {"yes", "y", "true", "1", "نعم", "اه", "أه", "ايوه", "أيوه", "تم", "موافق"}
NO_VALUES = {"no", "n", "false", "0", "لا", "لأ", "لم", "غير"}

# Navigation Pages
NAV_PAGES = [
    ("🏠", "Home", "home"),
    ("📊", "Team Performance", "team"),
    ("🔍", "Session Review Feedback", "b2c"),
    ("🎓", "Instructor Scheduler", "scheduler"),
    ("📅", "Bookings Attendance", "bookings"),
    ("💰", "Budget", "budget"),
]

# Home Dashboard Cards
DASHBOARD_CARDS = [
    {
        "icon": "📊",
        "title": "Team Performance",
        "desc": "Track employee tasks, hours logged, completion rates, late entries, and pipeline status.",
        "tags": ["Tasks", "Hours", "KPI", "Pipeline"],
        "color_key": "accent",
        "key": "team",
    },
    {
        "icon": "🎓",
        "title": "Instructor Scheduler",
        "desc": "Manage instructor schedules, detect conflicts, and assign new groups with availability checks.",
        "tags": ["Schedule", "Conflicts", "Groups", "Tracks"],
        "color_key": "green",
        "key": "scheduler",
    },
    {
        "icon": "🔍",
        "title": "Session Review Feedback",
        "desc": "Executive-level review dashboard for B2C & B2B sessions with recommendation and feedback analytics.",
        "tags": ["B2C", "Reviews", "Feedback", "Executive"],
        "color_key": "custom",
        "color": "#7f132d",
        "key": "b2c",
    },
    {
        "icon": "📅",
        "title": "Bookings Attendance",
        "desc": "Analyze bookings trends, status, and attendance metrics for merged Excel data.",
        "tags": ["Bookings", "Attendance", "Trends", "Metrics"],
        "color_key": "amber",
        "key": "bookings",
    },
]