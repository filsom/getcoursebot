from .router import starting_router
# from .dialog_with_free import (
#     free_starting_dialog, 
#     email_inpute_dialog, 
#     try_sub_dialog,
    
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
from .dialog_with_taining import trainings_dialog, new_training_dialog
from .dialog_with_food import input_kbju_dialog, food_dialog, calculate_kbju_dialog
from .dialog_with_day_menu import day_menu_dialog


starting_router.include_router(new_training_dialog)
starting_router.include_router(day_menu_dialog)
starting_router.include_router(calculate_kbju_dialog)
starting_router.include_router(food_dialog)
starting_router.include_router(input_kbju_dialog)
starting_router.include_router(admin_starting_dialog)
starting_router.include_router(trainings_dialog)
starting_router.include_router(paid_starting_dialog)
starting_router.include_router(upload_media_dialog)
starting_router.include_router(planed_mailling_dialog)
starting_router.include_router(send_mailings_dialog)
starting_router.include_router(mailing_dialog)
starting_router.include_router(content_bot_dialog)
starting_router.include_router(add_new_category_dialog)
starting_router.include_router(free_starting_dialog)
starting_router.include_router(anon_starting_dialog)