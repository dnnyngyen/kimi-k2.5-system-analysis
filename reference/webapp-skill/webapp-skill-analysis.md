# The WebApp Skill

The webapp-building skill provides a complete React development environment with TypeScript, Vite, Tailwind CSS, and shadcn/ui. Unlike document generation skills that produce files, this skill scaffolds entire applications with build pipelines and deployment configurations.

---

## Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Framework | React | 18+ |
| Language | TypeScript | 5+ |
| Build Tool | Vite | 5+ |
| Styling | Tailwind CSS | 3.4.19 |
| Components | shadcn/ui | Latest |
| UI Primitives | Radix UI | Various |

This stack was chosen for modern development patterns: fast HMR via Vite, type safety via TypeScript, utility-first styling via Tailwind, and accessible components via Radix/shadcn.

---

## shadcn/ui Components

The skill includes 50+ pre-installed shadcn/ui components organized by category:

**Layout**: `accordion`, `collapsible`, `resizable`, `scroll-area`, `separator`, `sidebar`, `skeleton`

**Forms**: `button`, `checkbox`, `input`, `input-otp`, `radio-group`, `select`, `slider`, `switch`, `textarea`, `calendar`, `form`

**Overlays**: `alert-dialog`, `command`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`, `hover-card`, `menubar`, `navigation-menu`, `popover`, `sheet`, `tooltip`

**Data Display**: `avatar`, `badge`, `card`, `carousel`, `chart`, `pagination`, `progress`, `table`, `tabs`, `toggle`, `toggle-group`

**Feedback**: `alert`, `empty`, `sonner`, `spinner`, `skeleton`

**Navigation**: `breadcrumb`, `kbd`, `label`, `pagination`

All components follow consistent patterns using Radix UI for accessibility, class-variance-authority for type-safe variants, and Tailwind for styling.

---

## Component Architecture

Components follow a standard pattern:

```typescript
// 1. Imports
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// 2. Variant definition with cva
const buttonVariants = cva(
  "base-classes",
  {
    variants: {
      variant: { /* ... */ },
      size: { /* ... */ },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

// 3. Component interface
export interface ButtonProps
  extends React.ComponentProps<"button">,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

// 4. Component implementation
const Button = React.forwardRef<
  HTMLButtonElement,
  ButtonProps
>(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    <Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

// 5. Exports
export { Button, buttonVariants }
```

---

## Button Component Example

The Button component demonstrates the full pattern:

```typescript
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white hover:bg-destructive/90",
        outline: "border bg-background shadow-xs hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md gap-1.5 px-3",
        lg: "h-10 rounded-md px-6",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

Variants: default (primary), destructive (delete), outline (secondary), secondary (alternative), ghost (subtle), link (navigation).

Sizes: default (36px), sm (32px), lg (40px), icon (36×36px).

---

## Initialization Workflow

```bash
# Step 1: Initialize project
bash /app/.kimi/skills/webapp-building/scripts/init-webapp.sh "Website Title"

# Output: /mnt/okcomputer/output/app/

# Step 2: Develop in src/
# Edit components, pages, hooks, types

# Step 3: Build
cd /mnt/okcomputer/output/app && npm run build

# Output: dist/ (index.html, assets/)

# Step 4: Deploy
deploy /mnt/okcomputer/output/app/dist/
```

---

## Path Aliases

The template configures `@/` to map to `src/`:

```typescript
// Instead of: import { Button } from "../../../components/ui/button"
import { Button } from "@/components/ui/button"
```

This is configured in `vite.config.ts` and `tsconfig.json`.

---

## Utility Functions

The `cn()` utility merges Tailwind classes with proper precedence:

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

Without `cn`: conflicting classes like `p-4 p-2` produce unpredictable results.
With `cn`: `cn("p-4", "p-2")` correctly resolves to `p-2`.

---

## Form Components

Forms use react-hook-form with Zod validation:

```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const formSchema = z.object({
  username: z.string().min(2),
})

function ProfileForm() {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "" },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `@radix-ui/react-*` | Headless UI primitives (accessibility, keyboard nav) |
| `class-variance-authority` | Type-safe variant definitions |
| `clsx` | Conditional class merging |
| `tailwind-merge` | Tailwind class deduplication |
| `@radix-ui/react-slot` | Polymorphic component support |
| `react-hook-form` | Form state management |
| `zod` | Schema validation |

---

## File Inventory

The webapp-building skill contains ~73 files in the template:
- `SKILL.md` — Workflow documentation
- `scripts/.prepare-template.sh` — Template preparation
- `scripts/init-webapp.sh` — Project initialization
- `scripts/template/` — Full React project scaffold
  - `src/components/ui/` — 50+ shadcn/ui components
  - `src/hooks/use-mobile.ts` — Mobile detection hook
  - `src/lib/utils.ts` — Utility functions
  - `src/App.tsx` — Main application
  - `package.json` — Dependencies
  - `vite.config.ts` — Build configuration
  - `tailwind.config.js` — Styling configuration
  - `tsconfig.json` — TypeScript configuration

Note: `node_modules/` contains ~26,082 files and is excluded from counts.
