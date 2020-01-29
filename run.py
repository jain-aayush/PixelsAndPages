from recommenderwebsite import create_app,db

app = create_app()
app.app_context().push()

if __name__ == '__main__':
	db.create_all(app=create_app())
	app.run(debug=True)