from .community import CommunityAddHandler, CommunityQueryHandler, CommunityDeleteHandler

urls = [
    ("/api/community/add", CommunityAddHandler),
    ("/api/community/query", CommunityQueryHandler),
    ("/api/community/delete", CommunityDeleteHandler),
]