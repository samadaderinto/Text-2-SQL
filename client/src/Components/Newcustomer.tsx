import { useState } from "react";
import { LuImagePlus } from "react-icons/lu";
import { Header } from "../layouts/Header";
import SideBar from "../layouts/SideBar";
import api from "../utils/api";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
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
    quantity: '',
    errors: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
      quantity: '',
    }
  });

  const validateForm = () => {
    const newErrors = {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      date: '',
      quantity: '',
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

    if (!formState.quantity || isNaN(Number(formState.quantity))) {
      newErrors.quantity = 'Valid quantity is required';
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

      try {
        await api.post(`/customers/create/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        nav('/customers')
        toast.success('Customer created successfully!', {
          position: "top-right",
        })


      } catch (error: any) {
        if (error.response && error.response.status === 400 && error.response.data.email) {
          toast.error('Email already exists. Please use a different email.', {
            position: "top-right"
          });
        } else {
          toast.error('Error creating customer. Please try again.');
        }
      }
    }
  };

  return (
    <>
      <Header />
      <SideBar />
      <div className="Newcustomer_Container">
        <h1>Create New Customer</h1>
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
                <span onClick={() => nav(-1)} className="Cancel_Btn">Cancel</span>
                <span onClick={handleCreateCustomer} className="Add_Btn">Add Customer</span>
              </div>
            </form>
          </div>
        </section>
      </div>
      <ToastContainer />
    </>
  )
}
