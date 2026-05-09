import os
import subprocess

frontend_dir = r"E:\project\shopconnect\frontend"
src_dir = os.path.join(frontend_dir, "src")

# 1. Install package
subprocess.run(["npm", "install", "react-phone-number-input"], cwd=frontend_dir, shell=True)

# 2. Update LoginPage.jsx
login_path = os.path.join(src_dir, "pages", "LoginPage.jsx")
with open(login_path, "r", encoding="utf-8") as f:
    login_content = f.read()

# Replace imports
login_content = login_content.replace(
    "import { useForm } from 'react-hook-form';",
    "import { useForm, Controller } from 'react-hook-form';\nimport PhoneInput, { isValidPhoneNumber } from 'react-phone-number-input';\nimport 'react-phone-number-input/style.css';"
)

# Replace schema
old_login_schema = """const loginSchema = z.object({
  phone: z.string().min(1, 'Le numéro de téléphone est requis'),
  password: z.string().min(1, 'Le mot de passe est requis'),
});"""
new_login_schema = """const loginSchema = z.object({
  phone: z.string().refine(isValidPhoneNumber, { message: 'Numéro de téléphone invalide' }),
  password: z.string().min(1, 'Le mot de passe est requis'),
});"""
login_content = login_content.replace(old_login_schema, new_login_schema)

# Add control to useForm
login_content = login_content.replace(
    "const { register, handleSubmit, formState: { errors } } = useForm({",
    "const { register, control, handleSubmit, formState: { errors } } = useForm({"
)

# Replace phone input block
old_login_phone_input = """          <div>
            <label className="block text-sm font-semibold text-text mb-2">Numéro de téléphone</label>
            <input
              type="text"
              {...register('phone')}
              placeholder="Ex: +257..."
              className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-error bg-error/10' : 'border-border bg-bg'} focus:outline-none focus:ring-2 focus:ring-primary transition-colors`}
            />
            {errors.phone && <p className="mt-2 text-sm text-error">{errors.phone.message}</p>}
          </div>"""

new_login_phone_input = """          <div>
            <label className="block text-sm font-semibold text-text mb-2">Numéro de téléphone</label>
            <Controller
              name="phone"
              control={control}
              render={({ field }) => (
                <PhoneInput
                  {...field}
                  defaultCountry="BI"
                  placeholder="Ex: 61 00 00 01"
                  className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-error bg-error/10' : 'border-border bg-bg'} focus-within:ring-2 focus-within:ring-primary transition-colors`}
                />
              )}
            />
            {errors.phone && <p className="mt-2 text-sm text-error">{errors.phone.message}</p>}
          </div>"""
login_content = login_content.replace(old_login_phone_input, new_login_phone_input)

with open(login_path, "w", encoding="utf-8") as f:
    f.write(login_content)

# 3. Update RegisterPage.jsx
register_path = os.path.join(src_dir, "pages", "RegisterPage.jsx")
with open(register_path, "r", encoding="utf-8") as f:
    register_content = f.read()

register_content = register_content.replace(
    "import { useForm } from 'react-hook-form';",
    "import { useForm, Controller } from 'react-hook-form';\nimport PhoneInput, { isValidPhoneNumber } from 'react-phone-number-input';\nimport 'react-phone-number-input/style.css';"
)

old_register_schema = """const registerSchema = z.object({
  first_name: z.string().min(1, 'Le prénom est requis'),
  last_name: z.string().min(1, 'Le nom est requis'),
  phone: z.string().min(1, 'Le numéro de téléphone est requis'),
  password: z.string().min(8, 'Le mot de passe doit contenir au moins 8 caractères'),
  confirm_password: z.string()
})"""
new_register_schema = """const registerSchema = z.object({
  first_name: z.string().min(1, 'Le prénom est requis'),
  last_name: z.string().min(1, 'Le nom est requis'),
  phone: z.string().refine(isValidPhoneNumber, { message: 'Numéro de téléphone invalide' }),
  password: z.string().min(8, 'Le mot de passe doit contenir au moins 8 caractères'),
  confirm_password: z.string()
})"""
register_content = register_content.replace(old_register_schema, new_register_schema)

register_content = register_content.replace(
    "const { register, handleSubmit, formState: { errors } } = useForm({",
    "const { register, control, handleSubmit, formState: { errors } } = useForm({"
)

old_register_phone_input = """          <div>
            <label className="block text-sm font-semibold text-text mb-2">Numéro de téléphone</label>
            <input
              type="text"
              {...register('phone')}
              placeholder="Ex: +257..."
              className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-error bg-error/10' : 'border-border bg-bg'} focus:outline-none focus:ring-2 focus:ring-primary`}
            />
            {errors.phone && <p className="mt-2 text-xs text-error">{errors.phone.message}</p>}
          </div>"""

new_register_phone_input = """          <div>
            <label className="block text-sm font-semibold text-text mb-2">Numéro de téléphone</label>
            <Controller
              name="phone"
              control={control}
              render={({ field }) => (
                <PhoneInput
                  {...field}
                  defaultCountry="BI"
                  placeholder="Ex: 61 00 00 01"
                  className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-error bg-error/10' : 'border-border bg-bg'} focus-within:ring-2 focus-within:ring-primary`}
                />
              )}
            />
            {errors.phone && <p className="mt-2 text-xs text-error">{errors.phone.message}</p>}
          </div>"""
register_content = register_content.replace(old_register_phone_input, new_register_phone_input)

with open(register_path, "w", encoding="utf-8") as f:
    f.write(register_content)

# 4. Append CSS for the inner input styling
css_append = """
/* React Phone Number Input Overrides */
.PhoneInputInput {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  outline: none;
  margin-left: 8px;
  color: var(--color-text);
  font-size: 1rem;
}
.PhoneInputCountry {
  padding-right: 8px;
  border-right: 1px solid var(--color-border);
}
"""
index_css_path = os.path.join(src_dir, "index.css")
with open(index_css_path, "a", encoding="utf-8") as f:
    f.write(css_append)

print("react-phone-number-input installed and implemented successfully.")
