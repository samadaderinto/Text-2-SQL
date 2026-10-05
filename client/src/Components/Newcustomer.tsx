import { useState } from "react";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/Sidebar";
import api from "../utils/api";
import { getApiErrorMessage } from "../utils/api-errors";
import { toast } from 'react-toastify';
import { useNavigate } from "react-router-dom";

export const NewCustomer = () => {
  const nav = useNavigate()
  const [formState, setFormState] = useState({
    img: null as string | null,
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    date: '',
    errors: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
    }
  });

  const validateForm = () => {
    const newErrors = {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
    };
    let valid = true;

    if (!formState.firstName) {
      newErrors.firstName = 'First name is required';
      valid = false;
    }
    if (!formState.lastName) {
      newErrors.lastName = 'Last Name is required';
      valid = false;
    }
    if (!formState.email) {
      newErrors.email = 'Email address is required';
      valid = false;
    }
    if (!formState.phone) {
      newErrors.phone = 'Phone number is required';
      valid = false;
    }
    setFormState({ ...formState, errors: newErrors });
    return valid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormState({
      ...formState,
      [e.target.name]: e.target.value,
      errors: {
        ...formState.errors,
        [e.target.name]: '',
      }
    });
  };

  const handleCreateCustomer = async () => {
    if (validateForm()) {
      const formData = new FormData();
      formData.append('first_name', formState.firstName);
      formData.append('last_name', formState.lastName);
      formData.append('email', formState.email);
      formData.append('phone_number', formState.phone);

      const toastId = toast.loading('Adding customer...');
      try {
        await api.post(`/customers/create/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        toast.update(toastId, {
          render: 'Customer added',
          type: 'success',
          isLoading: false,
          autoClose: 2200,
        });
        nav('/customers')

      } catch (error) {
        toast.update(toastId, {
          render: getApiErrorMessage(error, "Could not create the customer. Please try again."),
          type: 'error',
          isLoading: false,
          autoClose: 3200,
        });
      }
    }
  };

  return (
    <>
      <Header />
      <Sidebar />
      <div className="Newcustomer_Container">
        <header className="Form_Page_Header"><small className="Page_Eyebrow">AUDIENCE</small><h1>Add customer</h1><p>Create a customer profile for your store.</p></header>
        <section className="Product_Form_Container">
          <div className="GenProduct_Container">
            <h3>Customer Information</h3>
            <form>
              <label htmlFor="First_Name">First Name</label>
              <input
                type="text"
                name="firstName"
                placeholder="Input customer first name"
                id="First_Name"
                value={formState.firstName}
                onChange={handleChange}
              />
              {formState.errors.firstName && <p>{formState.errors.firstName}</p>}

              <label htmlFor="Last_Name">Last Name</label>
              <input
                type="text"
                name="lastName"
                id="Last_Name"
                placeholder="Input customer last name"
                value={formState.lastName}
                onChange={handleChange}
              />
              {formState.errors.lastName && <p>{formState.errors.lastName}</p>}

              <label htmlFor="customer_Email">Email</label>
              <input
                type="email"
                name="email"
                id="customer_Email"
                placeholder="Input customer email"
                value={formState.email}
                onChange={handleChange}
              />
              {formState.errors.email && <p>{formState.errors.email}</p>}

              <label htmlFor="customer_phone">Phone</label>
              <input
                type="tel"
                name="phone"
                id="customer_phone"
                placeholder="Input customer phone number"
                value={formState.phone}
                onChange={handleChange}
              />
              {formState.errors.phone && <p>{formState.errors.phone}</p>}

              <div>
                <button type="button" onClick={() => nav(-1)} className="Cancel_Btn">Cancel</button>
                <button type="button" onClick={handleCreateCustomer} className="Add_Btn">Add customer</button>
              </div>
            </form>
          </div>
        </section>
      </div>
    </>
  )
}
