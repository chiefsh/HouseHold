from .community import CommunityAddHandler, CommunityQueryHandler, CommunityDeleteHandler, CommunityIsTopHandler, CommunitySortHandler
urls = [
    ("/api/community/add", CommunityAddHandler),
    ("/api/community/query", CommunityQueryHandler),
    ("/api/community/delete", CommunityDeleteHandler),
    ("/api/community/up", CommunitySortHandler),
    ("/api/community/top", CommunityIsTopHandler),
]