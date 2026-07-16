import { Header } from "@/components/layout/Header";
import { UsersList } from "@/components/usuarios/UsersList";

export default function UsuariosPage() {
  return (
    <>
      <Header
        title="Usuarios"
        description="Gestión de usuarios registrados"
      />
      <div className="flex flex-col gap-6 p-6">
        <UsersList />
      </div>
    </>
  );
}
