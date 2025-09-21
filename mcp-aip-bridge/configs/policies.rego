package bridge

default allow = false

default redactions = []

allow {
  input.method != ""
}
