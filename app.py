from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

def find_static_and_templates():
    extra_dirs = ['templates', 'static']
    extra_files = []
    for d in extra_dirs:
        for dirname, _, files in os.walk(d):
            for filename in files:
                full_path = os.path.join(dirname, filename)
                extra_files.append(full_path)
    return extra_files

if __name__ == '__main__':
    app.run(debug=True, extra_files=find_static_and_templates())