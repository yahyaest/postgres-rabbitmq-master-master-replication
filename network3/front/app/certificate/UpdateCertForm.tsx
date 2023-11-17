"use client";
import React, { useState } from "react";
import { InputText } from "primereact/inputtext";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import axios from "axios";
import { useAtom } from "jotai";
import { certs } from "../../atoms";

export default function UpdateCertForm(props: any) {
  const { certificate } = props;
  const [certList, setCertList] = useAtom(certs);
  const [Owner, setOwner] = useState<string>(certificate.owner);
  const [visible, setVisible] = useState(false);
  const [CommonName, setCommonName] = useState<string>(certificate.common_name);
  const [SerialNumber, setSerialNumber] = useState<string>(
    certificate.serial_number
  );
  const [Fingerprint, setFingerprint] = useState<string>(
    certificate.fingerprint
  );
  const [CertB64, setCertB64] = useState<string>(certificate.cert_b64);
  const [ExpirationDate, setExpirationDate] = useState<string>(
    certificate.expiration_date
  );

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

  const UpdateForm = () => 
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
            onClick={() => updateCertificate()}
          >
            Update Certificate
          </button>
        </div>
      </div>
    </div>;
  ;

  const updateCertificate = async () => {
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
      const newCert = await axios.patch(
        `${djangoBaseUrl}/certificates/${certificate.id}/`,
        payload
      );
      let certsArray: any = [...certList];
      certsArray = certsArray.filter((cert: any) => cert.id !== certificate.id);
      console.log(newCert);
      certsArray = [...certsArray, newCert.data];
      certsArray = certsArray.sort((a: any, b: any) => a.id - b.id);
      setCertList(certsArray);
      setVisible(false);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="card flex justify-content-center">
      <Button
        label="Update"
        severity="warning"
        className="bg-yellow-400 p-2 text-sm hover:bg-yellow-300"
        rounded
        onClick={() => setVisible(true)}
      />
      <Dialog
        header={`Update certificate ${certificate.common_name}`}
        visible={visible}
        maximizable
        style={{ width: "50vw" }}
        onHide={() => setVisible(false)}
      >
        <UpdateForm />
      </Dialog>
    </div>
  );
}
