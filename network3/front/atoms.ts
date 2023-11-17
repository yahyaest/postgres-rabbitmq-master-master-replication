import {atom} from "jotai"

const certs = atom([])
const certsCount = atom(0)

export {certs, certsCount}