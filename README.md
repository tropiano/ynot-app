# Twitter Optimizer

To run the app

```
source release.sh

pythnon manage.py runserver
```

### Tailwind

To use Tailwind in development

```
npm run watch:css
```

Once development is over, build the `css` with

```
npm run build:css
```

This will create `static/mainapp/styles.css`. You can push this file in the repo.

### mainapp

The main app is where you will be putting your code.

Instead of typical files, like `views.py` or `models.py`, you'll find directories with similar names. These are Python
packages. The reason for this is that it's easier to split your code into multiple files this way.

Since we have only one app, we don't really need to create a separate `urls.py` file, so the whole URL configuration is
in `project/urls.py`. If you choose to have it separate, you can create a `urls.py` file in the `mainapp` directory and
import it in the `project/urls.py`
file. [Including other URLconfs](https://docs.djangoproject.com/en/5.0/topics/http/urls/#including-other-urlconfs)

### usermodel

This app holds the custom user model. It's a good idea to keep it separate from the main app, since it will be pretty
static and you won't be changing it often.

Custom User model has email as a login field.

The `email` field is case-insensitive. Also, the initial migration for this field is created with collation set to `db_collation=settings.CI_COLLATION` and `CI_COLLATION` is it `project/settings.py` depending on the database you are using.

## How to work on the project

Add your models in new files under `mainapp/models/` directory. Then add the model to `mainapp/models/__init__.py` file. This way you can split your models into multiple files.

Add your views in new files under `mainapp/views/` directory. Then add the view to `mainapp/views/__init__.py` file.

Add your forms in new files under `mainapp/forms/` directory. Then add the form to `mainapp/forms/__init__.py` file.

Templates for the app go into the root `templates` directory under `mainapp` subdirectory. For example, if you have a view `mainapp.views.home`, then the template should be at `templates/mainapp/home.html`.

The root template directory is great because you can override templates from other apps.
