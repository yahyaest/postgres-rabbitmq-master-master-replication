"use client";
import axios from "axios";
import { DataTable } from "primereact/datatable";
import { Paginator } from "primereact/paginator";
import { Column } from "primereact/column";
import { Button } from "primereact/button";
import CertForm from "./CertForm";
import { useAtom } from "jotai";
import { certs, certsCount } from "../../atoms";
import { useEffect, useState } from "react";
import { FaFileShield } from "react-icons/fa6";
import UpdateCertForm from "./UpdateCertForm";

export default function Certificate() {
  const [certList, setCertList] = useAtom(certs);
  const [certCount, setCertCount] = useAtom(certsCount);
  const [first, setFirst] = useState(0);

  const onPageChange = async (event) => {
    setFirst(event.first);
    const certificates: any = await getCertificates(event.page + 1);
    setCertList(certificates);
  };

  const getCertificates = async (page: number) => {
    try {
      const djangoBaseUrl = process.env.DJANGO_BASE_URL;
      console.log(djangoBaseUrl);
      const response = await axios.get(
        `${djangoBaseUrl}/certificates/?page=${page}`
      );
      setCertCount(response.data.count);
      setCertList(response.data.results);
      const certificates = response.data.results;
      return certificates.sort((a: any, b: any) => a.id - b.id);
    } catch (error) {
      console.error(error);
    }
  };

  const deleteCertificate = async (certificateId: number) => {
    try {
      const djangoBaseUrl = process.env.DJANGO_BASE_URL;
      console.log(djangoBaseUrl);
      await axios.delete(`${djangoBaseUrl}/certificates/${certificateId}/`);
      setCertCount(certCount - 1);
      setCertList(certList.filter((cert: any) => cert.id !== certificateId));
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    async function fetchData() {
      const certificates: any = await getCertificates(1);
      setCertList(certificates);
    }
    fetchData();
  }, []);

  const columns = [
    { field: "id", header: "Id" },
    { field: "owner", header: "Owner" },
    { field: "common_name", header: "Common Name" },
    { field: "serial_number", header: "Serial Number" },
    { field: "fingerprint", header: "Fingerprint" },
    { field: "cert_b64", header: "CertB64" },
    { field: "expiration_date", header: "Expiration Date" },
    { field: "update", header: "Update" },
    { field: "delete", header: "Delete" },
  ];

  return (
    <div className="flex flex-col">
      <header className="flex justify-between p-5 bg-blue-400">
        <div className="font-bold text-white">ENV_1</div>
        <div className="flex">
          <span className="font-bold text-white bg-red-500 rounded-full p-1 mx-2">
            {certList ? `${certCount}` : "0"}
          </span>
          <FaFileShield className="font-bold text-white mt-1" />
        </div>
      </header>
      <CertForm />

      <DataTable
        className="card w-3/4 mx-auto justify-center text-center"
        tableStyle={{ minWidth: "50rem" }}
        value={certList}
      >
        {columns.map((col) =>
          col.field !== "update" && col.field !== "delete" ? (
            <Column key={col.field} field={col.field} header={col.header} />
          ) : col.field !== "delete" ? (
            <Column
              key={col.field}
              body={(data, props) => <UpdateCertForm certificate={data} />}
              header={col.header}
            />
          ) : (
            <Column
              key={col.field}
              body={(data, props) => (
                <Button
                  label="Delete"
                  severity="danger"
                  className="bg-red-500 p-2 text-black text-sm hover:bg-red-400"
                  rounded
                  onClick={() => deleteCertificate(data.id)}
                />
              )}
              header={col.header}
            />
          )
        )}
      </DataTable>
      <div className="card pb-10">
        <Paginator
          first={first}
          rows={20}
          totalRecords={certCount}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
}
