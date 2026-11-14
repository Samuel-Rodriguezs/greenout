package formato

import (
	"math"
	"testing"
	"time"
)

func TestBytes(t *testing.T) {
	casos := []struct {
		in   int64
		want string
	}{
		{0, "0 B"},
		{1, "1 B"},
		{1023, "1023 B"},
		{1024, "1,0 KiB"},
		{1536, "1,5 KiB"},
		{1 << 20, "1,0 MiB"},
		{5 << 30, "5,0 GiB"},
		{-2048, "-2,0 KiB"},
		{math.MaxInt64, "8,0 EiB"},
		{math.MinInt64, "-8,0 EiB"},
	}
	for _, c := range casos {
		if got := Bytes(c.in); got != c.want {
			t.Errorf("Bytes(%d)=%q want %q", c.in, got, c.want)
		}
	}
}

func TestLerBytes(t *testing.T) {
	casos := []struct {
		in      string
		want    int64
		invalid bool
	}{
		{"0", 0, false},
		{"512", 512, false},
		{"512 B", 512, false},
		{"1KiB", 1024, false},
		{"1,5 KiB", 1536, false},
		{"1.5 kib", 1536, false},
		{"2MB", 2_000_000, false},
		{"2 MiB", 2 << 20, false},
		{"  3 GiB ", 3 << 30, false},
		{"-1 KiB", -1024, false},
		{"", 0, true},
		{"abc", 0, true},
		{"10 XB", 0, true},
		{"1 EiB x", 0, true},
		{"99999999999 PiB", 0, true},
	}
	for _, c := range casos {
		got, err := LerBytes(c.in)
		if (err != nil) != c.invalid {
			t.Errorf("LerBytes(%q) err=%v", c.in, err)
			continue
		}
		if !c.invalid && got != c.want {
			t.Errorf("LerBytes(%q)=%d want %d", c.in, got, c.want)
		}
	}
}

func TestBytesIdaEVolta(t *testing.T) {
	for _, n := range []int64{0, 1, 1024, 1 << 20, 3 << 30} {
		got, err := LerBytes(Bytes(n))
		if err != nil || got != n {
			t.Errorf("ida e volta %d -> %q -> %d (%v)", n, Bytes(n), got, err)
		}
	}
}

func TestDuracao(t *testing.T) {
	casos := []struct {
		in   time.Duration
		want string
	}{
		{0, "0s"},
		{500, "500ns"},
		{1500 * time.Nanosecond, "1µs"},
		{250 * time.Millisecond, "250ms"},
		{time.Second, "1s"},
		{1999 * time.Millisecond, "1s"},
		{time.Minute, "1min"},
		{90 * time.Second, "1min 30s"},
		{time.Hour + 2*time.Minute + 3*time.Second, "1h 2min 3s"},
		{25 * time.Hour, "1d 1h"},
		{48 * time.Hour, "2d"},
		{-90 * time.Second, "-1min 30s"},
		{-250 * time.Millisecond, "-250ms"},
		{time.Duration(math.MinInt64), "-106751d 23h 47min 16s"},
	}
	for _, c := range casos {
		if got := Duracao(c.in); got != c.want {
			t.Errorf("Duracao(%v)=%q want %q", c.in, got, c.want)
		}
	}
}
