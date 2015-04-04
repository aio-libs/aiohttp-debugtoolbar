<!DOCTYPE html>
<html>
    <head>
        <title>AJAX Test</title>
        <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
        <script src="http://code.jquery.com/jquery-migrate-1.2.1.min.js"></script>
    </head>
    <body>
        <h1>AJAX Test</h1>
        This page makes an AJAX request every 15 seconds.<br/><br/>
        <script>
            $(document).ready(function () {
                function _call() { $.get('${app.router['call_ajax'].url()}'); }
                setInterval(_call, 15000);
            });
        </script>
    </body>
</html>
