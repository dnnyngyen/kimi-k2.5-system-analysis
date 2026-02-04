# WebApp UI Components Analysis
## `/app/.kimi/skills/webapp-building/scripts/template/src/components/ui/` — shadcn/ui Component Library

---

## Executive Summary

The `ui/` directory contains 50+ pre-installed shadcn/ui components implementing a comprehensive React component library. These components provide headless UI primitives via Radix UI with customizable Tailwind CSS styling, following modern React patterns including composition, ref forwarding, and variant-based styling.

---

## 1. Component Inventory

### 1.1 By Category

| Category | Count | Components |
|----------|-------|------------|
| **Layout** | 7 | accordion, collapsible, resizable, scroll-area, separator, sidebar, skeleton |
| **Forms** | 12 | button, button-group, calendar, checkbox, form, input, input-group, input-otp, radio-group, select, slider, switch, textarea |
| **Overlays** | 12 | alert-dialog, command, context-menu, dialog, drawer, dropdown-menu, hover-card, menubar, navigation-menu, popover, sheet, tooltip |
| **Data Display** | 11 | avatar, badge, card, carousel, chart, pagination, progress, skeleton, table, tabs, toggle, toggle-group |
| **Feedback** | 5 | alert, empty, sonner, spinner, skeleton |
| **Navigation** | 4 | breadcrumb, kbd, label, pagination |

### 1.2 Complete List (50+ components)

```
accordion.tsx       alert-dialog.tsx    alert.tsx           aspect-ratio.tsx
avatar.tsx          badge.tsx           breadcrumb.tsx      button-group.tsx
button.tsx          calendar.tsx        card.tsx            carousel.tsx
chart.tsx           checkbox.tsx        collapsible.tsx     command.tsx
context-menu.tsx    dialog.tsx          drawer.tsx          dropdown-menu.tsx
empty.tsx           field.tsx           form.tsx            hover-card.tsx
input-group.tsx     input-otp.tsx       input.tsx           item.tsx
kbd.tsx             label.tsx           menubar.tsx         navigation-menu.tsx
pagination.tsx      popover.tsx         progress.tsx        radio-group.tsx
resizable.tsx       scroll-area.tsx     select.tsx          separator.tsx
sheet.tsx           sidebar.tsx         skeleton.tsx        slider.tsx
sonner.tsx          spinner.tsx         switch.tsx          table.tsx
tabs.tsx            textarea.tsx        toggle-group.tsx    toggle.tsx
tooltip.tsx
```

---

## 2. Component Architecture

### 2.1 Common Patterns

All shadcn/ui components follow consistent architectural patterns:

```typescript
// 1. Imports
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// 2. Variant definition with cva
const componentVariants = cva(
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
export interface ComponentProps
  extends React.ComponentProps<"element">,
    VariantProps<typeof componentVariants> {
  asChild?: boolean
}

// 4. Component implementation
const Component = React.forwardRef<
  HTMLElement,
  ComponentProps
>(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "element"
  return (
    <Comp
      className={cn(componentVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
})
Component.displayName = "Component"

// 5. Exports
export { Component, componentVariants }
```

### 2.2 Key Dependencies

| Package | Purpose |
|---------|---------|
| `@radix-ui/react-*` | Headless UI primitives (accessibility, keyboard nav) |
| `class-variance-authority` | Type-safe variant definitions |
| `clsx` | Conditional class merging |
| `tailwind-merge` | Tailwind class deduplication |
| `@radix-ui/react-slot` | Polymorphic component support |

---

## 3. Button Component Deep Dive

### 3.1 Full Implementation

```typescript
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline:
          "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost:
          "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
```

### 3.2 Variant Analysis

| Variant | Use Case | Styling |
|---------|----------|---------|
| `default` | Primary actions | Solid primary color |
| `destructive` | Delete, remove | Red background |
| `outline` | Secondary actions | Bordered, transparent bg |
| `secondary` | Alternative actions | Muted background |
| `ghost` | Subtle actions | Transparent, hover state |
| `link` | Navigation | Text-only with underline |

### 3.3 Size Analysis

| Size | Height | Padding | Use Case |
|------|--------|---------|----------|
| `default` | 36px | 16px horizontal | Standard buttons |
| `sm` | 32px | 12px horizontal | Compact UI |
| `lg` | 40px | 24px horizontal | Prominent actions |
| `icon` | 36×36px | — | Icon-only buttons |

---

## 4. Form Components

### 4.1 Form Component (with react-hook-form)

```typescript
import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { Slot } from "@radix-ui/react-slot"
import {
  Controller,
  FormProvider,
  useFormContext,
  useFormState,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from "react-hook-form"

import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"

const Form = FormProvider

// FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage
// ... implementation using react-hook-form context
```

### 4.2 Input Component

```typescript
import * as React from "react"
import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        className
      )}
      {...props}
    />
  )
}

export { Input }
```

---

## 5. Overlay Components

### 5.1 Dialog (Modal)

```typescript
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal
const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/50",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border p-6 shadow-lg duration-200 sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="ring-offset-background focus:ring-ring data-[state=open]:bg-accent data-[state=open]:text-muted-foreground absolute right-4 top-4 rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:pointer-events-none">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

export {
  Dialog, DialogPortal, DialogOverlay, DialogTrigger, DialogClose,
  DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription,
}
```

---

## 6. Data Display Components

### 6.1 Table Component

```typescript
import * as React from "react"
import { cn } from "@/lib/utils"

const Table = React.forwardRef<
  HTMLTableElement,
  React.HTMLAttributes<HTMLTableElement>
>(({ className, ...props }, ref) => (
  <div className="relative w-full overflow-auto">
    <table
      ref={ref}
      className={cn("w-full caption-bottom text-sm", className)}
      {...props}
    />
  </div>
))
Table.displayName = "Table"

const TableHeader = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn("[&_tr]:border-b", className)} {...props} />
))
TableHeader.displayName = "TableHeader"

const TableBody = React.forwardRef<
  HTMLTableSectionElement,
  React.HTMLAttributes<HTMLTableSectionElement>
>(({ className, ...props }, ref) => (
  <tbody
    ref={ref}
    className={cn("[&_tr:last-child]:border-0", className)}
    {...props}
  />
))
TableBody.displayName = "TableBody"

const TableRow = React.forwardRef<
  HTMLTableRowElement,
  React.HTMLAttributes<HTMLTableRowElement>
>(({ className, ...props }, ref) => (
  <tr
    ref={ref}
    className={cn(
      "hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors",
      className
    )}
    {...props}
  />
))
TableRow.displayName = "TableRow"

const TableHead = React.forwardRef<
  HTMLTableCellElement,
  React.ThHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <th
    ref={ref}
    className={cn(
      "text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props}
  />
))
TableHead.displayName = "TableHead"

const TableCell = React.forwardRef<
  HTMLTableCellElement,
  React.TdHTMLAttributes<HTMLTableCellElement>
>(({ className, ...props }, ref) => (
  <td
    ref={ref}
    className={cn(
      "p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
      className
    )}
    {...props}
  />
))
TableCell.displayName = "TableCell"

export {
  Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption
}
```

---

## 7. Utility Functions

### 7.1 cn() — Class Name Merging

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Purpose**: Merge Tailwind classes with proper precedence handling.

**Example**:
```tsx
// Without cn: conflicting classes
className="p-4 p-2"  // Unpredictable

// With cn: resolved
className={cn("p-4", "p-2")}  // p-2 wins
```

---

## 8. Component Usage Patterns

### 8.1 Basic Button

```tsx
import { Button } from "@/components/ui/button"

<Button>Click me</Button>
<Button variant="destructive">Delete</Button>
<Button size="sm" variant="outline">Small</Button>
```

### 8.2 Form with Validation

```tsx
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

### 8.3 Dialog

```tsx
import {
  Dialog, DialogTrigger, DialogContent, DialogHeader,
  DialogTitle, DialogDescription
} from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

---

## 9. Code Metrics

| Metric | Value |
|--------|-------|
| Total Components | 50+ |
| Average Lines per Component | ~50-100 |
| Dependencies | Radix UI, Tailwind, cva, clsx, tailwind-merge |
| Bundle Size Impact | Tree-shakeable |

---

*Document Version: 1.0*
*Analysis Date: 2026-02-02*
