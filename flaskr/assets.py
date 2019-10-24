from flask_assets import Bundle

# REGISTRY FOR CASCADING STYLESHEETS AND JAVASCRIPT ###########################

# Add more assets below, as-needed.
# No need to edit the templates for that.
# Add your additional css in `common`, not under `css`.
# --> (relative paths hack fix, gotta go fast)

common_css = Bundle(
    'css/vendor/bootstrap.min.css',
    'css/vendor/helper.css',
    'css/common/main.css',
    filters='cssmin',
    output='public/css/common.css'
)

common_js = Bundle(
    'js/vendor/jquery-3.2.1.slim.min.js',
    'js/vendor/popper.min.js',
    'js/vendor/bootstrap.min.js',
    Bundle(
        'js/main.js',
        filters='jsmin'
    ),
    output='public/js/common.js'
)
