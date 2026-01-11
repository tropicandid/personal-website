from app import init_app


app = init_app()

# #TODO:
# 1. Remove unneccessary routes from the app file
# 2. Remove unnecessary template files
# 3. Make sure contents are modularized into 02-components as much as possible
# 4. Write content for site
# 5. Source Photos for pages
# 6. Create db structures and editability for site

if __name__ == "__main__":
    app.run(debug=True)