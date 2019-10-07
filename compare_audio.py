import pyaudio


def main():
    chunk = 1024
    a_format = pyaudio.paInt16
    channels = 2
    rate = 44100
    record_seconds = 5

    p = pyaudio.PyAudio()

    try:
        stream = p.open(
            format=a_format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
            input_device_index=2
        )

        frames = []

        for i in range(0, int(rate / chunk * record_seconds) + 1):
            data = stream.read(chunk)
            frames.append(data)

        tot = 0
        num = 0
        for x in range(len(frames)):
            for y in frames[x]:
                amp_sample3 = abs(frames[x][y])
                tot += amp_sample3
                num += 1

        average = tot/num

        stream.stop_stream()
        stream.close()
        p.terminate
    except OSError:
        average = 100

    if average > 120.00:
        return 1
    else:
        return 0




