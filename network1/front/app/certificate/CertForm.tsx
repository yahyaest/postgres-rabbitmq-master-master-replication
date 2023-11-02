"use client";
import React, { useState } from "react";
import { InputText } from "primereact/inputtext";
import axios from "axios";
import { useAtom } from "jotai";
import { certs, certsCount } from "../../atoms";

export default function CertForm() {
  const [Owner, setOwner] = useState<string>("");
  const [CommonName, setCommonName] = useState<string>("");
  const [SerialNumber, setSerialNumber] = useState<string>("");
  const [Fingerprint, setFingerprint] = useState<string>("");
  const [CertB64, setCertB64] = useState<string>("");
  const [ExpirationDate, setExpirationDate] = useState<string>("");
  const [certList, setCertList] = useAtom(certs);
  const [certCount, setCertCount] = useAtom(certsCount);


  const fields = [
    { key: "owner", value: Owner, label: "Owner" },
    { key: "common_name", value: CommonName, label: "Common Name" },
    { key: "serial_number", value: SerialNumber, label: "Serial Number" },
    { key: "fingerprint", value: Fingerprint, label: "Fingerprint" },
    { key: "cert_b64", value: CertB64, label: "CertB64" },
    { key: "expiration_date", value: ExpirationDate, label: "Expiration Date" },
  ];

  const setInput = (
    input: React.ChangeEvent<HTMLInputElement>,
    field: string
  ) => {
    if (field === "owner") {
      setOwner(input.target.value);
    } else if (field === "common_name") {
      setCommonName(input.target.value);
    } else if (field === "serial_number") {
      setSerialNumber(input.target.value);
    } else if (field === "fingerprint") {
      setFingerprint(input.target.value);
    } else if (field === "cert_b64") {
      setCertB64(input.target.value);
    } else if (field === "expiration_date") {
      setExpirationDate(input.target.value);
    }
  };

  const postCertificate = async () => {
    try {
      const payload = {
        owner: Owner,
        common_name: CommonName,
        serial_number: SerialNumber,
        fingerprint: Fingerprint,
        cert_b64: CertB64,
        expiration_date: ExpirationDate,
      };

      const djangoBaseUrl = process.env.DJANGO_BASE_URL;
      const newCert = await axios.post(`${djangoBaseUrl}/certificates/`, payload);
      let certsArray: any = [...certList, newCert.data];
      setCertList(certsArray);
      setCertCount(certCount + 1)
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm mb-5">
      <div className="space-y-6">
        {fields.map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-medium leading-6 text-gray-900">
              {field.label}
            </label>
            <div className="card flex justify-content-center">
              <InputText
                value={field.value}
                onChange={(e) => setInput(e, field.key)}
              />
            </div>
          </div>
        ))}

        <div>
          <button
            className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            onClick={() => postCertificate()}
          >
            Post Certificate
          </button>
        </div>
      </div>
    </div>
  );
}
