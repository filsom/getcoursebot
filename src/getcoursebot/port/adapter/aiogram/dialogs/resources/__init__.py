from .router import starting_router
# from .dialog_with_free import (
#     free_starting_dialog, 
#     email_inpute_dialog, 
#     try_sub_dialog,
    
# )
from .dialog_with_free_user import (
    anon_starting_dialog,
    free_starting_dialog
)
from .dialog_with_paid_user import paid_starting_dialog
from .dialog_with_admin import (
    add_access_dialog, 
    users_groups_dialog, 
    admin_starting_dialog, 
    close_access_dialog,
    content_bot_dialog,
    add_new_category_dialog
)
from .dialog_with_mailings import send_mailings_dialog, mailing_dialog, planed_mailling_dialog
from .dialog_with_upload_media import upload_media_dialog


# starting_router.include_router(free_starting_dialog)
# starting_router.include_router(email_inpute_dialog)
starting_router.include_router(admin_starting_dialog)
starting_router.include_router(paid_starting_dialog)
starting_router.include_router(upload_media_dialog)
starting_router.include_router(planed_mailling_dialog)
starting_router.include_router(send_mailings_dialog)
starting_router.include_router(mailing_dialog)
# starting_router.include_router(content_bot_dialog)
# starting_router.include_router(add_new_category_dialog)
# starting_router.include_router(mailling_dialog)
# starting_router.include_router(planed_mailling_dialog)

starting_router.include_router(free_starting_dialog)
starting_router.include_router(anon_starting_dialog)