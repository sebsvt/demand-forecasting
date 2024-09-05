package logs

import (
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var log *zap.Logger

func init() {
	config := zap.NewDevelopmentEncoderConfig()
	config.TimeKey = "timestamp"
	config.EncodeTime = zapcore.ISO8601TimeEncoder
	config.StacktraceKey = ""

	// Console encoder
	consoleEncoder := zapcore.NewConsoleEncoder(config)

	// Console writer
	consoleWriter := zapcore.Lock(os.Stdout)

	fileEncoder := zapcore.NewJSONEncoder(config)
	logFile, _ := os.OpenFile("log.json", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	fileWriter := zapcore.AddSync(logFile)

	defaultLogLevel := zapcore.InfoLevel

	// Create a core with both file and console writers
	core := zapcore.NewTee(
		zapcore.NewCore(fileEncoder, fileWriter, defaultLogLevel),
		zapcore.NewCore(consoleEncoder, consoleWriter, defaultLogLevel),
	)

	log = zap.New(core, zap.AddCallerSkip(1))
}

func Info(msg string, fields ...zapcore.Field) {
	log.Info(msg, fields...)
}

func Debug(msg string, fields ...zapcore.Field) {
	log.Debug(msg, fields...)
}

func Error(msg interface{}, fields ...zapcore.Field) {
	switch v := msg.(type) {
	case error:
		log.Error(v.Error(), fields...)
	case string:
		log.Error(v, fields...)
	}
}
