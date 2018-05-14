/**
 * Created by Rene on 6/26/2015.
 */
//    Parameters
//    ----------
//    speed: Frequency with which the timer gets updated in ms.
//    $element: HTML element at which the timer should be displayed.
var Timer = (function () {

    function Timer(speed, $element) {
        this.speed = speed;
        this.startTime = 0;
        this.totalPauseTime = 0;
        this.newPauseStartTime = 0;
        this.$element = $element;
        this.isPause = false;
        this.isRunning = false;
        this.endTime = 0;
    }

    Timer.prototype =  {
        Start: function () {
            this.isPause = false;
            this.isRunning = true;
            this.startTime = new Date().getTime();
            this.totalPauseTime = 0;
            this.newPauseStartTime = 0;
            window.setTimeout(Loop.bind(this), this.speed)
        },

        Resume: function () {
            if (this.isPause) {
                this.isPause = false;
                this.isRunning = true;
                this.totalPauseTime += CalculatePauseElapsedTime.call(this);
                console.log("pause time was " + this.totalPauseTime);
                window.setTimeout(Loop.bind(this), this.speed)
            }
        },

        IsRunning: function () {
              return this.isRunning;
        },

        Pause: function () {
            this.isRunning = false;
            this.isPause = true;
            this.newPauseStartTime = new Date().getTime();
        },

        GetElapsedTime: function() {
            if (this.startTime == 0) {
                return 0;
            } else if (this.totalPauseTime > this.endTime) {    // User
                // chose label and then paused and afterwards submitted
                return this.endTime;
            } else {
                // User chose label, potentially paused, and changed his/her
                // mind
                return this.endTime - this.totalPauseTime;
            }
        },

        GetCurrentTime: function() {
            if (this.startTime == 0) {
                return 0;
            } else if (this.isPause) {
                return CalculateTotalElapsedTime.call(this) - CalculatePauseElapsedTime.call(this);
            } else {
                return CalculateTotalElapsedTime.call(this);
            }
        },

        Stop: function () {
            this.endTime = new Date().getTime() - this.startTime;
            console.log("new endtime: " + (this.endTime - this.totalPauseTime));
        },

        SetSpeed: function (speed) {
            this.speed = speed;
        },

        ResetTimer: function() {
            this.startTime = 0;
            this.totalPauseTime = 0;
            this.newPauseStartTime = 0;
            this.isPause = false;
            this.isRunning = false;
            this.endTime = 0;
            this.$element.html(msToTime(0));
        }
    };

    function CalculateTotalElapsedTime () {
        return new Date().getTime() - this.startTime - this.totalPauseTime;
    }

    function CalculatePauseElapsedTime() {
        return new Date().getTime() - this.newPauseStartTime;
    }

    function Loop () {
        var diff = CalculateTotalElapsedTime.call(this);
        this.$element.html(msToTime(diff));
        if (!this.isPause) {
             window.setTimeout(Loop.bind(this), this.speed)
        }
    }

    function msToTime(s) {

      function addZ(n) {
        return (n<10? '0':'') + n;
      }

      var ms = s % 1000;
      s = (s - ms) / 1000;
      var secs = s % 60;
      s = (s - secs) / 60;
      var mins = s % 60;
      var hrs = (s - mins) / 60;

      return addZ(hrs) + ':' + addZ(mins) + ':' + addZ(secs) + '.' + ms;
    }

    return Timer;

}());
