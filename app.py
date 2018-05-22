from flask import Flask, request, render_template
import server_utils
import router

###############################################
SERVER_ERR_MSGS = {
    server_utils.NAME_ERR: "your name input is too long. The character limit is 100.",
    server_utils.NUM_ERR: "the phone number you input isn't valid.",
    server_utils.TIME_ERR: "your time input was corrupted somehow. Refreshing might help.",
    server_utils.SUBMIT_ERR: "your submission was corrupted, somehow. Refreshing might help.",
}
###############################################

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def homepage():
    print(request.method)
    print(request.form)

    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        name = request.form["name"]
        number = request.form["phone"]
        time = request.form["time"]
        submit_type = request.form["submit_type"]

        twilio_client = router.twilio_client
        err_code = server_utils.validate_inputs(name, number, twilio_client, time, submit_type)

        if err_code == server_utils.NO_ERR:
            pass
        else:
            err_msg = SERVER_ERR_MSGS[err_code]
            return render_template("err.html", err_msg=err_msg)

        timestr = server_utils.parse_time(time)
        if submit_type == server_utils.TRY:
            router.run_once(name, number)
            return render_template("try.html", number=number)
        if submit_type == server_utils.SUB:
            router.add_db_entry(name, number, timestr)
            router.send_sub_confirmation(name, number, time)
            return render_template("sub.html", name=name)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)