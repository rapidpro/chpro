============================
Working with CSS and Theming
============================

The chpro dashboard has a custom flask-appbuilder CSS theme applied to it.
You can view it by visiting ``/static/appbuilder/css/themes/rph.css``. You may modify this theme
simply by duplicating the current ``rph.css`` file and updating the theme setting in ``superset_config.py``::


    APP_THEME = "rph.css"


In the ``rph.css`` file, you will find a set of CSS variables that will allow you to easily do a basic theming of the dashboard. Of course, you can also write your own styles if you need more customization.
These are the values that are available to customize for a quick and easy theme::


    --color-primary: var(--color-pink);
    --color-secondary: var(--color-navy);
    --color-background: var(--color-yellow-light);

    --header-font: 'Titillium Web', Helvetica, sans-serif;
    --body-font: 'Open Sans', Helvetica, sans-serif;
    --weight-bold: 700;


For more information on theming Superset, please use the resources below:

* https://flask-appbuilder.readthedocs.io/en/latest/customizing.html
* https://flask-appbuilder.readthedocs.io/en/latest/templates.html
