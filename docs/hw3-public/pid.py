class PID:
    def __init__(
            self, gain_prop: float, gain_int: float, gain_der: float, sensor_period: float,
            output_limits: tuple[float, float]
            ):
        self.gain_prop = gain_prop
        self.gain_der = gain_der
        self.gain_int = gain_int
        self.sensor_period = sensor_period
        # TODO: define additional attributes you might need
        self.integral = 0
        self.min_output, self.max_output = output_limits
        # END OF TODO


    # TODO: implement function which computes the output signal
    # The controller should output only in the range of output_limits
    def output_signal(self, commanded_variable: float, sensor_readings: list[float]) -> float:
        error = sensor_readings[0] - commanded_variable
        self.integral += error * self.sensor_period
        derivative = (sensor_readings[0] - sensor_readings[1]) / self.sensor_period
        output = self.gain_prop * error + self.gain_der * derivative + self.gain_int * self.integral
        return max(self.min_output, min(self.max_output, output))
    # END OF TODO
